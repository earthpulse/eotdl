import lightning as L
from glob import glob
import geopandas as gpd
from torch.utils.data import DataLoader
import numpy as np
from sklearn.model_selection import train_test_split

from .ds import ClassificationDataset

def get_classification_labels(images, labels, classes):
    classification_labels = []
    remove = []
    for ix, label in enumerate(labels):
        _label = gpd.read_file(label)
        classification = _label[_label['task'] == 'classification']
        if len(classification) > 0:
            cls = classification.label.values
            cls = [classes.index(i) for i in cls if i in classes]
            _classes = np.zeros(len(classes), dtype=int)
            _classes[cls] = 1
            classification_labels.append(_classes)
            if len(cls) == 0:
                remove.append(ix)
                # print(f'{label} has no valid classification label')
                continue
        else:
            classification_labels.append(np.zeros(len(classes)))
            remove.append(ix)
            # print(f'{label} has no classification label')
    images = [i for ix, i in enumerate(images) if ix not in remove]
    classification_labels = [i for ix, i in enumerate(classification_labels) if ix not in remove]
    return images, classification_labels

class SCANEOClassificationDataModule(L.LightningDataModule):
    def __init__(self, 
            path, 
            classes = [], 
            batch_size=16, 
            num_workers=4, 
            pin_memory=True, 
            val_split=0.2, 
            train_trans=None, 
            val_trans=None
        ):
        super().__init__()
        self.path = path
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.train_trans = train_trans
        self.val_trans = val_trans
        self.val_split = val_split
        self.classes = classes
        self.num_classes = len(classes)

    def setup(self, stage=None):
        if len(self.classes) == 0:
            raise ValueError('a list of classes must be provided')
        labels = sorted(glob(f'{self.path}/*.geojson'))
        images = [i.replace('geojson', 'tif') for i in labels]
        images, classification_labels = get_classification_labels(images, labels, self.classes)
        train_image, val_image, train_label, val_label = train_test_split(images, classification_labels, test_size=self.val_split, random_state=42)
        print("Training on", len(train_image), "images")
        print("Validating on", len(val_image), "images")
        self.train_ds = ClassificationDataset(train_image, train_label, trans=self.train_trans)
        self.val_ds = ClassificationDataset(val_image, val_label, trans=self.val_trans)

    def train_dataloader(self, batch_size=None, shuffle=True):
        return DataLoader(
            self.train_ds, 
            batch_size=batch_size or self.batch_size, 
            num_workers=self.num_workers, 
            pin_memory=self.pin_memory,
            shuffle=shuffle
        )

    def val_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(
            self.val_ds, 
            batch_size=batch_size or self.batch_size, 
            num_workers=self.num_workers, 
            pin_memory=self.pin_memory,
            shuffle=shuffle
        )
