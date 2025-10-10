import lightning as L
import albumentations as A
from lightning.pytorch.loggers import CSVLogger
from lightning.pytorch.callbacks import ModelCheckpoint

from eotdl.pytorch.segmentation import SegmentationDataModule, SegmentationModule

train_trans = A.Compose([
    A.RandomCrop(width=128, height=128),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.Transpose(p=0.5),
], is_check_shapes=False)

dm = SegmentationDataModule(
    'data/MassachusettsRoadsS2/tiff', 
    batch_size=8, 
    train_source_path='train_s2', 
    val_source_path='val_s2', 
    train_labels_path='train_s2_labels', 
    val_labels_path='val_s2_labels', 
    test_source_path='test_s2', 
    test_labels_path='test_s2_labels', 
    train_trans=train_trans, 
    val_trans=A.CenterCrop(width=128, height=128), 
    test_trans=A.CenterCrop(width=128, height=128),
    source_ext='.tiff',
    label_ext='.tif',
)

module = SegmentationModule(lr=3e-4, num_classes=1)

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