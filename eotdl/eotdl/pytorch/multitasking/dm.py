from glob import glob
import json
from sklearn.model_selection import train_test_split

from .ds import MultiTaskDataset
from ..classification.dm import SCANEOClassificationDataModule, get_classification_labels

class SCANEOMultiTaskDataModule(SCANEOClassificationDataModule):
    def __init__(self, 
            path, 
            classes, 
            batch_size=16, 
            num_workers=4, 
            pin_memory=True, 
            val_split=0.2, 
            train_trans=None, 
            val_trans=None):
        super().__init__(
            path=path,
            classes=classes,
            batch_size=batch_size,
            num_workers=num_workers,
            pin_memory=pin_memory,
            val_split=val_split,
            train_trans=train_trans,
            val_trans=val_trans
        )
        self.classification_classes = classes
        self.num_cls_classes = len(classes)
        with open(f'{path}/spai.json', 'r') as f:
            self.spai_labels = json.load(f)
        self.classes = [label['name'] for label in self.spai_labels['labels']]
        self.num_seg_classes = len(self.classes) + 1
        self.colors = {label['name']: label['color'] for label in self.spai_labels['labels']}

    def setup(self, stage=None):
        masks = sorted(glob(f'{self.path}/*_mask.tif'))
        images = [i.replace('_mask.tif', '.tif') for i in masks]
        labels = [i.replace('tif', 'geojson') for i in images]
        images, classification_labels = get_classification_labels(images, labels, self.classification_classes)
        train_image, val_image, train_label, val_label = train_test_split(images, classification_labels, test_size=self.val_split, random_state=42)
        train_mask = [i.replace('.tif', '_mask.tif') for i in train_image]
        val_mask = [i.replace('.tif', '_mask.tif') for i in val_image]
        print("Training on", len(train_image), "images")
        print("Validating on", len(val_image), "images")
        self.train_ds = MultiTaskDataset(train_image, train_mask, train_label, trans=self.train_trans, num_classes=self.num_seg_classes)
        self.val_ds = MultiTaskDataset(val_image, val_mask, val_label, trans=self.val_trans, num_classes=self.num_seg_classes)