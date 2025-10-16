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
