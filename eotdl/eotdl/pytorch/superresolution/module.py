import lightning as L
import torch.nn as nn
import torch
from torchmetrics.image import PeakSignalNoiseRatio, StructuralSimilarityIndexMeasure
import os 

from .model import ESRT

class ESRTModule(L.LightningModule):
	def __init__(self, upscale = 2, pretrained = None):
		super().__init__()
		self.save_hyperparameters()
		self.model = ESRT(upscale=upscale)
		self.loss = nn.L1Loss()
		self.train_psnr = PeakSignalNoiseRatio(data_range=1.0)
		self.train_ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
		self.val_psnr = PeakSignalNoiseRatio(data_range=1.0)
		self.val_ssim = StructuralSimilarityIndexMeasure(data_range=1.0)
		if pretrained:
			self.load_pretrained(pretrained)

	def forward(self, x):
		return self.model(x)
	
	def predict(self, x):
		self.eval()
		with torch.no_grad():
			return self.model(x.to(self.device))
	
	def training_step(self, batch, batch_idx):
		x, y = batch
		y_hat = self(x)
		loss = self.loss(y_hat, y)
		psnr = self.train_psnr(y_hat, y)
		ssim = self.train_ssim(y_hat, y)
		self.log("train_loss", loss, prog_bar=True)
		self.log("train_psnr", psnr, prog_bar=True)
		self.log("train_ssim", ssim, prog_bar=True)
		return loss
	
	def validation_step(self, batch, batch_idx):
		x, y = batch
		y_hat = self(x)
		loss = self.loss(y_hat, y)
		psnr = self.val_psnr(y_hat, y)
		ssim = self.val_ssim(y_hat, y)
		self.log("val_loss", loss, prog_bar=True, sync_dist=True)
		self.log("val_psnr", psnr, prog_bar=True, sync_dist=True)
		self.log("val_ssim", ssim, prog_bar=True, sync_dist=True)

	def configure_optimizers(self):
		optimizer = torch.optim.AdamW(self.model.parameters(), lr=3e-4, weight_decay=1e-4)
		scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=200, gamma=0.5)
		return [optimizer], [scheduler]
	
	def load_pretrained(self, path):
		if os.path.isfile(path):
			print("===> loading model '{}'".format(path))
			checkpoint = torch.load(path)['state_dict']
			model_dict = self.model.state_dict()
			pretrained_dict = {k.replace('model.', ''): v for k, v in checkpoint.items()}
			for k, v in model_dict.items():
				if k not in pretrained_dict:
					print(k)
			self.model.load_state_dict(pretrained_dict, strict=True)
		else:
			print("===> no models found at '{}'".format(path))
