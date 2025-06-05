import torch 
import skimage.io as io
from einops import rearrange
import numpy as np
from skimage.transform import resize
from skimage import exposure

class Dataset(torch.utils.data.Dataset):
	def __init__(
			self, 
			hr_paths, 
			lr_paths, 
			upscale = 2, 
			trans = None,
			hr_bands=(0, 1, 2, 3), 	# R G B Nir satellogic
			lr_bands=(3, 2, 1, 7) 	# R G B Nir Sentinel 2
		):
		self.hr_paths = hr_paths
		self.lr_paths = lr_paths
		self.upscale = upscale
		self.trans = trans
		self.hr_bands = hr_bands
		self.lr_bands = lr_bands
		
	def __len__(self):
		return len(self.hr_paths)
	
	def __getitem__(self, idx):
		try:
			hr = io.imread(self.hr_paths[idx])[..., self.hr_bands].astype(np.float32)
		except Exception as e:
			print(f"Error loading HR image {self.hr_paths[idx]}: {e}")
			return self.__getitem__(0)
		try:
			lr = io.imread(self.lr_paths[idx])[..., self.lr_bands].astype(np.float32)
		except Exception as e:
			print(f"Error loading LR image {self.lr_paths[idx]}: {e}")
			return self.__getitem__(0)
		if self.trans: # flips and crops
			trans = self.trans(image=hr, image2=lr)
			hr = trans["image"]
			lr = trans["image2"]
		hr = exposure.match_histograms(hr, lr, channel_axis=-1)
		# normalize
		hr = np.clip(hr / 4000, 0, 1)
		lr = np.clip(lr / 4000, 0, 1)
		# center crop satellogic at 380x380 (original size is 384x384) and lr at 38x38
		hr = hr[2:-2, 2:-2, :]
		h, w = lr.shape[:2]
		lr = lr[h//2-19:h//2+19, w//2-19:w//2+19, :]
		# resize according to the upscale factor
		target_size = 38 * self.upscale
		# make sure 380 is divisible by the upscale factor
		# if 380 % self.upscale != 0:
		# 	raise ValueError(f"Target size {target_size} is not divisible by the upscale factor {self.upscale}")
		hr = resize(hr, (target_size, target_size), order=3, anti_aliasing=False)
		# channels first
		hr = rearrange(hr, "h w c -> c h w")
		lr = rearrange(lr, "h w c -> c h w")
		return lr, hr#, hr0