import lightning as L
from glob import glob
import os
import numpy as np
import albumentations as A
from torch.utils.data import DataLoader

from .ds import Dataset

IGONRE_ZONES = [ # después de insepcción visual, estas zonas creo que no aportan mucho
    '33S',
    '39N',
    '55N',
    '44N',
    '28N',
    '40N',
    '49N',
    '34N',
    '11N',
    '12N',
    '50S',
    '57N',
    '18S',
    '17N',
    '53N',
    '34S',
    '19N',
    '36N',
    '35N',
    '45N',
    '17S',
    '20N',
    '41N',
    '21N',
    '52N',
    '60S',
    '32S',
    '19S',
    '54N',
    '53S',
    '04N',
    '27N',
    '25S',
    '08N',
    '37S',
    '09N',
    '43S',
    '52S'
]

class ESRTDatamodule(L.LightningDataModule):
	def __init__(
			self, 
			path = "/fastdata/Satellogic/data/tifs", 
			upscale = 2,
			batch_size = 16, 
			val_size = 0.2,
			seed = 2025,
			num_workers = 20,
			pin_memory = True,
			train_samples = None
		):
		super().__init__()
		self.path = path
		self.batch_size = batch_size
		self.num_workers = num_workers
		self.val_size = val_size
		self.seed = seed
		self.num_workers = num_workers
		self.pin_memory = pin_memory
		self.upscale = upscale
		self.train_samples = train_samples

	def setup(self, stage = None):
		np.random.seed(self.seed)
		hr_paths = glob(self.path + "/satellogic/*.tif")
		hr_paths = [p for p in hr_paths if not any(zone in p for zone in [f"_{zone}_" for zone in IGONRE_ZONES])]
		remove = []
		for path in hr_paths:
			lr_path = path.replace("satellogic", "sentinel2").replace("_TOA.tif", "_S2L2A.tiff")
			if not os.path.exists(lr_path):
				remove.append(path)
		hr_paths = [p for p in hr_paths if p not in remove]
		if self.train_samples is not None:
			hr_paths = hr_paths[:self.train_samples]
		print(f"Found {len(hr_paths)} images (removed {len(remove)} images)")
		np.random.shuffle(hr_paths)
		val_size = int(len(hr_paths) * self.val_size)
		hr_train_paths = hr_paths[:-val_size]
		hr_val_paths = hr_paths[-val_size:]
		print(f"Using {len(hr_train_paths)} training images and {len(hr_val_paths)} validation images")
		lr_train_paths = self.generate_lr_paths(hr_train_paths)
		lr_val_paths = self.generate_lr_paths(hr_val_paths)
		assert len(hr_train_paths) == len(lr_train_paths), "Number of hr and lr images must be the same"
		assert len(hr_val_paths) == len(lr_val_paths), "Number of hr and lr images must be the same"
		# for path in lr_train_paths + lr_val_paths:
		# 	assert os.path.exists(path), f"LR image {path} does not exist"
		trans = A.Compose([
			A.HorizontalFlip(),
			A.VerticalFlip(),
			A.Transpose(),
			A.RandomRotate90(),
		], additional_targets={"image2": "image"}, is_check_shapes=False)
		self.train_ds = Dataset(hr_train_paths, lr_train_paths, self.upscale, trans)
		self.val_ds = Dataset(hr_val_paths, lr_val_paths, self.upscale)
		
	def generate_lr_paths(self, hr_paths):
		return [
			f.replace("satellogic", "sentinel2").replace("_TOA.tif", "_S2L2A.tiff")
			for f in hr_paths
		]
		
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
