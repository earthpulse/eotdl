import lightning as L
import numpy as np
import albumentations as A
from torch.utils.data import DataLoader

from .ds import Dataset

class ESRTDatamodule(L.LightningDataModule):
	def __init__(
			self, 
			hr_paths, 
			lr_paths, 
			upscale = 2,
			batch_size = 16, 
			val_size = 0.2,
			seed = 2025,
			num_workers = 20,
			pin_memory = True,
			train_samples = None,
			resize = True,
			hr_bands=(0, 1, 2, 3), 	
			lr_bands=(3, 2, 1, 7),
		):
		super().__init__()
		self.hr_paths = hr_paths
		self.lr_paths = lr_paths
		self.batch_size = batch_size
		self.num_workers = num_workers
		self.val_size = val_size
		self.seed = seed
		self.num_workers = num_workers
		self.pin_memory = pin_memory
		self.upscale = upscale
		self.train_samples = train_samples
		self.resize = resize
		self.hr_bands = hr_bands
		self.lr_bands = lr_bands

	def setup(self, stage = None):
		np.random.seed(self.seed)
		assert len(self.hr_paths) == len(self.lr_paths), "Number of hr and lr images must be the same"
		if self.train_samples is not None:
			self.hr_paths = self.hr_paths[:self.train_samples]
			self.lr_paths = self.lr_paths[:self.train_samples]
		ixs = np.arange(len(self.hr_paths))
		np.random.shuffle(ixs)
		val_size = int(len(ixs) * self.val_size)
		train_ixs = ixs[:-val_size]
		val_ixs = ixs[-val_size:]
		hr_train_paths, hr_val_paths = np.array(self.hr_paths)[train_ixs], np.array(self.hr_paths)[val_ixs]
		lr_train_paths, lr_val_paths = np.array(self.lr_paths)[train_ixs], np.array(self.lr_paths)[val_ixs]
		print(f"Using {len(hr_train_paths)} training images and {len(hr_val_paths)} validation images")
		assert len(hr_train_paths) == len(lr_train_paths), "Number of hr and lr images must be the same"
		assert len(hr_val_paths) == len(lr_val_paths), "Number of hr and lr images must be the same"
		trans = A.Compose([
			A.HorizontalFlip(),
			A.VerticalFlip(),
			A.Transpose(),
			A.RandomRotate90(),
		], additional_targets={"image2": "image"}, is_check_shapes=False)
		self.train_ds = Dataset(hr_train_paths, lr_train_paths, self.hr_bands, self.lr_bands,  self.upscale, trans, resize=self.resize)
		self.val_ds = Dataset(hr_val_paths, lr_val_paths, self.hr_bands, self.lr_bands, self.upscale, resize=self.resize)
		
	def get_dataloader(self, dataset, batch_size = None, shuffle = False):
		return DataLoader(
			dataset,
			batch_size=batch_size if batch_size is not None else self.batch_size,
			num_workers=self.num_workers,
			pin_memory=self.pin_memory,
			shuffle=shuffle if shuffle is not None else True
		)
	
	def train_dataloader(self, batch_size = None, shuffle = True):
		return self.get_dataloader(self.train_ds, batch_size, shuffle)
	
	def val_dataloader(self, batch_size = None, shuffle = False):
		return self.get_dataloader(self.val_ds, batch_size, shuffle)
