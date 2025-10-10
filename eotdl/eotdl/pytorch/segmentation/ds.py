import rasterio as rio
import numpy as np
from torch.utils.data import Dataset
import torch

class SegmentationDataset(Dataset):
    def __init__(self, images, masks, bands=[1,2,3], norm_value = 4000, trans=None, num_classes=6):
        self.images = images
        self.masks = masks
        self.trans = trans
        self.bands = bands
        self.norm_value = norm_value
        self.num_classes = num_classes
        
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = rio.open(self.images[idx]).read(self.bands)
        image = np.clip(image / self.norm_value, 0, 1).transpose(1,2,0)
        mask = rio.open(self.masks[idx]).read(1)
        if self.trans is not None:
            trans = self.trans(image=image, mask=mask)
            image, mask = trans['image'], trans['mask']
        return torch.from_numpy(image.transpose(2,0,1)).float(), \
            torch.nn.functional.one_hot(torch.from_numpy(mask).long(), num_classes=self.num_classes).float().permute(2,0,1)
    
class BinarySegmentationDataset(torch.utils.data.Dataset):
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
    