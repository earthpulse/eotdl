import matplotlib.pyplot as plt
import requests
import numpy as np

import datetime
import torch.nn as nn


def download_github_directory(api_url, local_dir):
    response = requests.get(api_url)
    if response.status_code != 200:
        raise RuntimeError(f"GitHub API request failed: {response.status_code}")
    
    items = response.json()
    for item in items:
        if item['type'] == 'file':
            # Download file
            download_url = item['download_url']
            local_file = local_dir / item['name']
            print(f"Downloading {download_url} -> {local_file}")
            r = requests.get(download_url)
            r.raise_for_status()
            with open(local_file, 'wb') as f:
                f.write(r.content)
        elif item['type'] == 'dir':
            # Recurse into subfolder
            subfolder = local_dir / item['name']
            subfolder.mkdir(exist_ok=True)
            download_github_directory(item['url'], subfolder)
            
def plot_s2_natural_color(ds, stretch=True, percentile=(2, 98), figsize=(10, 10)):
    """
    Plot Sentinel-2 natural color composite (RGB = B4, B3, B2).
    
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing bands "B2", "B3", and "B4".
    stretch : bool, optional
        Apply contrast stretching (default=True).
    percentile : tuple, optional
        Percentile limits for contrast stretching (default=(2, 98)).
    figsize : tuple, optional
        Figure size.
    """

    # Extract RGB bands and convert to numpy
    try:
        r = ds['B4'].values.astype(np.float32)
        g = ds['B3'].values.astype(np.float32)
        b = ds['B2'].values.astype(np.float32)
    except KeyError:
        raise KeyError("Dataset must contain bands 'B2', 'B3', and 'B4' for natural color.")

    # Stack into RGB array
    rgb = np.stack([r, g, b], axis=-1)

    # Handle possible scaling (e.g., reflectance scaled by 10000)
    if np.nanmax(rgb) > 1.5:  # assume raw reflectance (0–10000)
        rgb /= 10000.0

    # Clip invalid values
    rgb = np.clip(rgb, 0, 1)

    # Optional contrast stretching per channel
    if stretch:
        rgb_stretched = np.zeros_like(rgb)
        for i in range(3):
            p_low, p_high = np.nanpercentile(rgb[..., i], percentile)
            rgb_stretched[..., i] = np.clip((rgb[..., i] - p_low) / (p_high - p_low), 0, 1)
        rgb = rgb_stretched

    # Plot
    plt.figure(figsize=figsize)
    plt.imshow(rgb)
    plt.axis('off')
    plt.title("Sentinel-2 Natural Color (RGB = B4, B3, B2)")
    plt.show()
    


def normalize_dataframe(df, config):
    '''
    Normalizes specific columns in a dataframe based on a provided 
    configuration dictionary of min/max values.
    
    Args:
        df (pd.DataFrame): The input dataframe.
        config (dict): A dictionary where keys are column names and 
                       values are tuples of (min_val, max_val).
                       
    Returns:
        pd.DataFrame: A new dataframe with normalized values.
    '''
    # Create a copy to avoid SettingWithCopy warnings on the original df
    df_norm = df.copy()
    
    for col_name, (min_val, max_val) in config.items():
        # Check if the column exists in the dataframe before trying to normalize
        if col_name in df_norm.columns:
            # Apply Min-Max normalization formula
            df_norm[col_name] = (df_norm[col_name] - min_val) / (max_val - min_val)
        else:
            print(f'Warning: Column "{col_name}" found in config but not in DataFrame.')
            
    return df_norm


def model_to_net(model, input_config, output_config, input_names, output_names, filename='custom_c2rcc_pytorch.net'):
    '''
    Exports a trained PyTorch model to the specific ASCII .net format required by ESA SNAP.
    
    Args:
        model (nn.Module): The trained PyTorch model.
        input_config (dict): Dictionary of inputs {'col_name': (min_val, max_val)}.
        output_config (dict): Dictionary of outputs {'col_name': (min_val, max_val)}.
        input_names (list): Ordered list of input names.
        output_names (list): Ordered list of output names.
        filename (str): Output filename.
    '''
    
    # Ensure model is in eval mode to prevent any training flags affecting weights
    model.eval()

    # --- 1. EXTRACT RANGES FROM CONFIG ---
    in_min = []
    in_max = []
    
    for name in input_names:
        if name not in input_config:
            raise ValueError(f'Input "{name}" required by model but missing from input_config.')
        mn, mx = input_config[name]
        in_min.append(mn)
        in_max.append(mx)

    out_min = []
    out_max = []
    
    for name in output_names:
        if name not in output_config:
            raise ValueError(f'Output "{name}" required by model but missing from output_config.')
        mn, mx = output_config[name]
        
        # Handle Dummy Outputs (Flat Ranges)
        if mn == mx:
            mn = 0.0
            mx = 1.0
            
        out_min.append(mn)
        out_max.append(mx)

    # Identify Linear Layers
    # Assuming 'model.layers' is your nn.Sequential block from the previous code
    # If using a different structure, use [m for m in model.modules() if isinstance(m, nn.Linear)]
    linear_layers = [l for l in model.layers if isinstance(l, nn.Linear)]

    # --- 2. WRITE FILE ---
    with open(filename, 'w') as f:
        
        # --- HEADER ---
        f.write(f'problem: Custom C2RCC Training (PyTorch Export)\n')
        f.write(f'saved at {datetime.datetime.now().strftime("%c")}\n\n')
        f.write('trainings sample has total sum of error^2=1.0\n')
        f.write('average of residues:\n training 0.01 test 0.01\n ratio avg.train/avg.test=1.0\n\n')

        # --- INPUT/OUTPUT DEFINITIONS ---
        f.write(f'the net has {len(input_names)} inputs:\n')
        for i, name in enumerate(input_names):
            f.write(f'input  {i+1} is {name} in [{in_min[i]:.6f},{in_max[i]:.6f}]\n')
        
        f.write(f'\nthe net has {len(output_names)} outputs:\n')
        for i, name in enumerate(output_names):
            f.write(f'output  {i+1} is {name} in [{out_min[i]:.6f},{out_max[i]:.6f}]\n')

        # --- RANGES REPEAT BLOCK ---
        f.write('\nranges repeated for easier input\n#\n')
        f.write(f'{len(input_names)}\n')
        for i in range(len(input_names)):
            f.write(f'{in_min[i]:.6f} {in_max[i]:.6f}\n')
        f.write(f'{len(output_names)}\n')
        for i in range(len(output_names)):
            f.write(f'{out_min[i]:.6f} {out_max[i]:.6f}\n')
        
        f.write('$\n') 

        # --- TOPOLOGY ---
        # PyTorch Linear layers store output features in .out_features
        layer_sizes = [len(input_names)] + [l.out_features for l in linear_layers]
        topo_str = ' '.join(map(str, layer_sizes))
        f.write(f'#planes={len(layer_sizes)} {topo_str}\n')

        # --- BIASES ---
        for i, layer in enumerate(linear_layers):
            # Extract bias, move to cpu, convert to numpy
            biases = layer.bias.detach().cpu().numpy()
            
            f.write(f'bias {i+1} {len(biases)}\n')
            for b in biases:
                f.write(f'{b:.6f}\n')

        # --- WEIGHTS ---
        for i, layer in enumerate(linear_layers):
            # PyTorch stores weights as [Output, Input]
            weights = layer.weight.detach().cpu().numpy()
            
            # Note: PyTorch shape is (out_features, in_features)
            # This matches SNAP's expectation (Node-Major), so NO transpose is needed here.
            output_dim = weights.shape[0]
            input_dim = weights.shape[1]
            
            f.write(f'wgt {i} {input_dim} {output_dim}\n')
            
            # Flatten (row-major default is correct here because shape is [Out, In])
            flat_weights = weights.flatten() 
            for w in flat_weights:
                f.write(f'{w:.6f}\n')

    print(f'Successfully exported PyTorch model to: {filename}')