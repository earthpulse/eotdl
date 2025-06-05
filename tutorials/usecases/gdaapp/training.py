import lightning as L
import albumentations as A
from lightning.pytorch.loggers import CSVLogger
from lightning.pytorch.callbacks import ModelCheckpoint

from src.dm import DataModule
from src.module import Module

trans = A.Compose([
    A.CenterCrop(width=128, height=128),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.Transpose(p=0.5),
], is_check_shapes=False)

dm = DataModule(
    'data/MassachusettsRoadsS2/tiff', 
    batch_size=8, 
    train_trans=trans, val_trans=trans, test_trans=trans)

module = Module(lr=3e-4)

trainer = L.Trainer(
    max_epochs=100,
    accelerator='gpu',
    devices=1,
    precision = "bf16-mixed",
    logger=CSVLogger('logs', name='gdaapp'),
    callbacks=[
        ModelCheckpoint(
            dirpath='checkpoints',
            monitor='val_iou',
            mode='max',
            save_top_k=1,
            save_last=True,
            filename='{epoch}-{val_iou:.4f}'
        )
    ]
)

trainer.fit(module, dm)