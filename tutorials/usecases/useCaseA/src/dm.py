import lightning as L
from glob import glob
from torch.utils.data import DataLoader
import albumentations as A
import os
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

from .ds import Dataset, EuroSATDataset

class ToGray(A.ImageOnlyTransform):
    def __init__(self, p=0.5):
        super().__init__(p=p)
        
    def apply(self, img, **params):
        gray = np.mean(img[:,:,:3], axis=2, keepdims=True)
        return np.repeat(gray, img.shape[2], axis=2).astype(img.dtype)

class DataModule(L.LightningDataModule):
    def __init__(self, path, bands=(1,2,3,4), batch_size=256, num_workers=20, pin_memory=True, trans=None, norm_value=4000):
        super().__init__()
        self.path = path
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.trans = trans
        self.norm_value = norm_value
        self.bands = bands
        self.pin_memory = pin_memory

    def setup(self, stage=None):
        print("Unsupervised")
        images = glob(f'{self.path}/*')
        print(f"Number of images: {len(images)}")
        self.df = pd.DataFrame(images, columns=['image'])
        self.ds = Dataset(
            images,
            A.Compose([
                A.RandomResizedCrop(size=(224, 224), scale=(0.5, 1.0)),
                A.HorizontalFlip(),
                A.VerticalFlip(),
                A.Rotate(),
                A.Transpose(),
                # A.ColorJitter(), # expects RGB images
                # A.ToGray(), # expects RGB images
                ToGray(),
                A.GaussianBlur(p=0.3),
            ]),
            self.bands,
            self.norm_value
        )

    def train_dataloader(self, batch_size=None, shuffle=True):
        return DataLoader(
            self.ds,
            batch_size=batch_size or self.batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )

class EuroSATDataModule(L.LightningDataModule):
    def __init__(self, path, bands=(4,3,2,8), norm_value=4000, batch_size=32, num_workers=10, label_ratio=1., pin_memory=True):
        super().__init__()
        self.path = path
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.label_ratio = label_ratio
        self.pin_memory = pin_memory
        self.bands = bands
        self.norm_value = norm_value

    def setup(self, stage=None):
        # get labels from folder structure if not provided
        self.labels = sorted(os.listdir(self.path))
        print("EuroSAT")
        print("Generating images and labels ...")
        images, encoded = [], []
        for ix, label in enumerate(self.labels):
            _images = os.listdir(f'{self.path}/{label}')
            images += [f'{self.path}/{label}/{img}' for img in _images]
            encoded += [ix]*len(_images)
        print(f'Number of images: {len(images)}')
        # train / val split
        print("Generating train / val splits ...")
        train_images, val_images, train_labels, val_labels = train_test_split(
            images,
            encoded,
            stratify=encoded,
            test_size=0.2,
            random_state=42
        )
        # filter by label ratio
        if self.label_ratio < 1. and self.label_ratio > 0.:
            train_images_ratio, train_labels_ratio = [], []
            unique_labels = np.unique(train_labels)
            for label in unique_labels:
                filter = np.array(train_labels) == label
                ixs = filter.nonzero()[0]
                num_samples = filter.sum()
                ratio_ixs = np.random.choice(
                    ixs, int(self.label_ratio*num_samples), replace=False)
                train_images_ratio += (np.array(train_images)
                                       [ratio_ixs]).tolist()
                train_labels_ratio += (np.array(train_labels)
                                       [ratio_ixs]).tolist()
            train_images = train_images_ratio
            train_labels = train_labels_ratio
        self.train_ds = EuroSATDataset(train_images, train_labels, self.bands, self.norm_value)
        self.val_ds = EuroSATDataset(val_images, val_labels, self.bands, self.norm_value)
        print("Training samples: ", len(self.train_ds))
        print("Validation samples: ", len(self.val_ds))

    def train_dataloader(self, batch_size=None, shuffle=True):
        return DataLoader(
            self.train_ds,
            batch_size=batch_size or self.batch_size,
            num_workers=self.num_workers,
            shuffle=shuffle,
            pin_memory=self.pin_memory,
        )

    def val_dataloader(self, batch_size=None, shuffle=False):
        return DataLoader(
            self.val_ds,
            batch_size=batch_size or self.batch_size,
            num_workers=self.num_workers,
            shuffle=shuffle,
            pin_memory=self.pin_memory
        )
