import lightning as L
import os
from torch.utils.data import DataLoader

from .ds import Dataset

class DataModule(L.LightningDataModule):
    def __init__(self, root, batch_size=16, num_workers=4, pin_memory=True, train_trans=None, val_trans=None, test_trans=None, bands=(4,3,2), norm_value=4000):
        super().__init__()
        self.root = root
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.train_trans = train_trans
        self.val_trans = val_trans
        self.test_trans = test_trans
        self.bands = bands
        self.norm_value = norm_value

    def setup(self, stage=None):
        train_images = sorted(os.listdir(os.path.join(self.root, 'train_s2')))
        val_images = sorted(os.listdir(os.path.join(self.root, 'val_s2')))
        test_images = sorted(os.listdir(os.path.join(self.root, 'test_s2')))
        train_images_paths = [os.path.join(self.root, 'train_s2', image) for image in train_images]
        val_images_paths = [os.path.join(self.root, 'val_s2', image) for image in val_images]
        test_images_paths = [os.path.join(self.root, 'test_s2', image) for image in test_images]
        train_labels_paths = [os.path.join(self.root, 'train_s2_labels', image.replace('.tiff', '.tif')) for image in train_images]
        val_labels_paths = [os.path.join(self.root, 'val_s2_labels', image.replace('.tiff', '.tif')) for image in val_images]
        test_labels_paths = [os.path.join(self.root, 'test_s2_labels', image.replace('.tiff', '.tif')) for image in test_images]
        self.train_ds = Dataset(train_images_paths, train_labels_paths, self.train_trans, self.bands, self.norm_value)
        self.val_ds = Dataset(val_images_paths, val_labels_paths, self.val_trans, self.bands, self.norm_value)
        self.test_ds = Dataset(test_images_paths, test_labels_paths, self.test_trans, self.bands, self.norm_value)

    def train_dataloader(self, batch_size=None, shuffle=True):
        return DataLoader(self.train_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)

    def val_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(self.val_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)
    
    def test_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(self.test_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)