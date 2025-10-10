from glob import glob
import json

from .ds import SegmentationDataset
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

