import rasterio as rio
import numpy as np
from torch.utils.data import Dataset
import torch

class ClassificationDataset(Dataset):
    def __init__(self, images, labels, bands=[1,2,3], norm_value = 4000, trans=None):
        self.images = images
        self.labels = labels
        self.trans = trans
        self.bands = bands
        self.norm_value = norm_value

    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = rio.open(self.images[idx]).read(self.bands)
        image = np.clip(image / self.norm_value, 0, 1).transpose(1,2,0)
        if self.trans is not None:
            image = self.trans(image=image)['image']
        labels = self.labels[idx]
        return torch.from_numpy(image.transpose(2,0,1)).float(), torch.from_numpy(labels).float()
    

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
    

class MultiTaskDataset(Dataset):
    def __init__(self, images, masks, labels, bands=[1,2,3], norm_value = 4000, trans=None, num_classes=6):
        self.images = images
        self.masks = masks
        self.labels = labels
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
        label = self.labels[idx]
        if self.trans is not None:
            trans = self.trans(image=image, mask=mask)
            image, mask = trans['image'], trans['mask']
        return torch.from_numpy(image.transpose(2,0,1)).float(), \
            torch.nn.functional.one_hot(torch.from_numpy(mask).long(), num_classes=self.num_classes).float().permute(2,0,1), \
            torch.from_numpy(label).float()
    

