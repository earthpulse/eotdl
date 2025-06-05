import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint, LearningRateMonitor
from lightning.pytorch.loggers import CSVLogger
from src.module import ESRTModule
from src.dm import ESRTDatamodule
import torch

UPSCALE = 2
BATCH_SIZE = 16
EPOCHS = 100
PRETRAINED = None #"checkpoints/esrt_wss2_epoch=241.ckpt"

dm = ESRTDatamodule(upscale = UPSCALE, batch_size = BATCH_SIZE, train_samples = 10000)
module = ESRTModule(upscale = UPSCALE, pretrained = PRETRAINED)

torch.set_float32_matmul_precision('medium')

trainer = L.Trainer(
	accelerator = "gpu",
	devices = 1,
	precision = "bf16-mixed",
	max_epochs = EPOCHS,
	callbacks = [
		ModelCheckpoint(
			monitor = "val_loss",
			mode = "min",
			save_top_k = 1,
			filename = "esrt_ws_{epoch:03d}_{val_loss:.5f}",
			dirpath = "checkpoints",
		),
		ModelCheckpoint(
			monitor = "val_psnr",
			mode = "max",
			save_top_k = 1,
			filename = "esrt_ws_{epoch:03d}_{val_psnr:.5f}",
			dirpath = "checkpoints",
		),
        ModelCheckpoint(
			monitor = "val_ssim",
			mode = "max",
			save_top_k = 1,
			filename = "esrt_ws_{epoch:03d}_{val_ssim:.5f}",
			dirpath = "checkpoints",
		),
		ModelCheckpoint(
			monitor = "epoch",
			mode = "max",
			save_top_k = 1,
			filename = "esrt_ws_{epoch:03d}",
			dirpath = "checkpoints",
		),
		LearningRateMonitor(logging_interval = "step"),
	],
	logger = CSVLogger(save_dir = "logs", name = f"esrt_{UPSCALE}x"),
)

trainer.fit(module, dm)
