from glob import glob
import json
import os
from torch.utils.data import DataLoader
import lightning as L

from .ds import SegmentationDataset, BinarySegmentationDataset
from ..classification.dm import SCANEOClassificationDataModule
    
class SCANEOSegmentationDataModule(SCANEOClassificationDataModule):
    def __init__(self, 
            path, 
            batch_size=16, 
            num_workers=4, 
            pin_memory=True, 
            val_split=0.2, 
            train_trans=None, 
            val_trans=None
        ):
        super().__init__(
            path=path,
            batch_size=batch_size,
            num_workers=num_workers,
            pin_memory=pin_memory,
            val_split=val_split,
            train_trans=train_trans,
            val_trans=val_trans
        )
        with open(f'{path}/spai.json', 'r') as f:
            self.spai_labels = json.load(f)
        self.classes = [label['name'] for label in self.spai_labels['labels']]
        self.num_classes = len(self.classes) + 1
        self.colors = {label['name']: label['color'] for label in self.spai_labels['labels']}

    def setup(self, stage=None):
        masks = sorted(glob(f'{self.path}/*_mask.tif'))
        images = [i.replace('_mask.tif', '.tif') for i in masks]
        val_size = int(len(images) * self.val_split)
        train_image = images[:-val_size]
        val_image = images[-val_size:]
        train_mask = masks[:-val_size]
        val_mask = masks[-val_size:]
        print("Training on", len(train_image), "images")
        print("Validating on", len(val_image), "images")
        self.train_ds = SegmentationDataset(train_image, train_mask, trans=self.train_trans, num_classes=self.num_classes)
        self.val_ds = SegmentationDataset(val_image, val_mask, trans=self.val_trans, num_classes=self.num_classes)

class SegmentationDataModule(L.LightningDataModule):
    def __init__(self, root, train_source_path, val_source_path, train_labels_path, val_labels_path, test_source_path=None, test_labels_path=None, batch_size=5, num_workers=4, pin_memory=True, train_trans=None, val_trans=None, test_trans=None, bands=(4,3,2), norm_value=4000, source_ext=".tiff", label_ext=".tif"):
        super().__init__()
        self.root = root
        self.train_source_path = train_source_path
        self.val_source_path = val_source_path
        self.test_source_path = test_source_path
        self.train_labels_path = train_labels_path
        self.val_labels_path = val_labels_path
        self.test_labels_path = test_labels_path  
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.train_trans = train_trans
        self.val_trans = val_trans
        self.test_trans = test_trans
        self.bands = bands
        self.norm_value = norm_value
        self.source_ext = source_ext
        self.label_ext = label_ext

    def setup(self, stage=None):
        train_images = sorted(os.listdir(os.path.join(self.root, self.train_source_path)))
        val_images = sorted(os.listdir(os.path.join(self.root, self.val_source_path)))
        if self.test_source_path is not None:
            test_images = sorted(os.listdir(os.path.join(self.root, self.test_source_path)))
        train_images_paths = [os.path.join(self.root, self.train_source_path, image) for image in train_images]
        val_images_paths = [os.path.join(self.root, self.val_source_path, image) for image in val_images]
        if self.test_source_path is not None:
            test_images_paths = [os.path.join(self.root, self.test_source_path, image) for image in test_images]
        train_labels_paths = [os.path.join(self.root, self.train_labels_path, self.change_ext(image, self.source_ext, self.label_ext)) for image in train_images]
        val_labels_paths = [os.path.join(self.root, self.val_labels_path, self.change_ext(image, self.source_ext, self.label_ext)) for image in val_images]
        test_labels_paths = [os.path.join(self.root, self.test_labels_path, self.change_ext(image, self.source_ext, self.label_ext)) for image in test_images]
        self.train_ds = BinarySegmentationDataset(train_images_paths, train_labels_paths, self.train_trans, self.bands, self.norm_value)
        self.val_ds = BinarySegmentationDataset(val_images_paths, val_labels_paths, self.val_trans, self.bands, self.norm_value)
        self.test_ds = BinarySegmentationDataset(test_images_paths, test_labels_paths, self.test_trans, self.bands, self.norm_value)

    def change_ext(self, p, ext1, ext2):
        if ext1 != ext2:
            return p.replace(ext1, ext2) 
        return p

    def train_dataloader(self, batch_size=None, shuffle=True):
        return DataLoader(self.train_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)

    def val_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(self.val_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)
    
    def test_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(self.test_ds, batch_size=batch_size or self.batch_size, shuffle=shuffle, num_workers=self.num_workers, pin_memory=self.pin_memory)