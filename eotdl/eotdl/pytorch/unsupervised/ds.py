import torch 
import rasterio as rio
import numpy as np
from skimage import io


class Dataset(torch.utils.data.Dataset):
    def __init__(self, images, trans, bands, norm_value=4000):
        self.images = images
        self.trans = trans
        self.bands = bands
        self.norm_value = norm_value

    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        with rio.open(self.images[idx]) as image_src:
            image = np.clip(image_src.read(self.bands) / self.norm_value, 0, 1).astype(np.float32).transpose(1, 2, 0)
        if self.trans:
            # get two random augmented version of image 
            # random cropping, resizing, horizontal flipping, color jittering, converting to grayscale, Gaussian blurring, and solarization
            image1 = self.trans(image=image)['image']
            image2 = self.trans(image=image)['image']
        return torch.from_numpy(image1).float().permute(2, 0, 1), torch.from_numpy(image2).float().permute(2, 0, 1)
    
class EuroSATDataset(torch.utils.data.Dataset):
    def __init__(self, images, labels, bands, norm_value=4000):
        self.images = images
        self.labels = labels
        self.bands = [b - 1 for b in bands]
        self.norm_value = norm_value
    
    def __len__(self):
        return len(self.images)

    def __getitem__(self, ix):
        img = io.imread(self.images[ix])[..., self.bands]
        img = torch.from_numpy(
            img / self.norm_value).clip(0, 1).float().permute(2, 0, 1)
        label = torch.tensor(self.labels[ix], dtype=torch.long)
        return img, label
