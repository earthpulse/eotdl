import torch 
import rasterio as rio
import numpy as np


class Dataset(torch.utils.data.Dataset):
    def __init__(self, images, masks, trans=None, bands=(4,3,2), norm_value=4000):
        self.images = images
        self.masks = masks
        self.trans = trans
        self.bands = bands
        self.norm_value = norm_value

    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        with rio.Env(CPL_LOG_LEVEL='ERROR'):
            with rio.open(self.images[idx]) as image_src:
                image = np.clip(image_src.read(self.bands) / self.norm_value, 0, 1).astype(np.float32).transpose(1, 2, 0)
            with rio.open(self.masks[idx]) as mask_src:
                mask = (mask_src.read(1) / 255.0).astype(np.float32)
        
        if self.trans:
            trans = self.trans(image=image, mask=mask)
            image, mask = trans['image'].transpose(2, 0, 1), trans['mask']
        return torch.from_numpy(image).float(), torch.from_numpy(mask).float().unsqueeze(0)
    
    