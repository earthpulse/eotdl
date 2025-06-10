from src.dm import EuroSATDataModule
from src.module import EuroSATModule, Module
import timm
import lightning as L
from lightning.pytorch.loggers import CSVLogger

BACKBONE = 'resnet34'
BANDS = (4,3,2,8)
CKPT = 'checkpoints/epoch=64-loss=142.12485.ckpt'
MAX_EPOCHS = 20
LABEL_RATIOS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

experiments = [
    ('scratch', False, False),
    ('imagenet-ft', True, False),
    ('imagenet-tl', True, True),
    ('ssl-ft', False, False),
    ('ssl-tl', False, True),
]

for experiment in experiments:
    name, pretrained, freeze = experiment
    for label_ratio in LABEL_RATIOS:
        print(f'Running experiment {name} with label ratio {label_ratio}...')
        dm = EuroSATDataModule(
            '/fastdata/EuroSAT/ds/images/remote_sensing/otherDatasets/sentinel_2/tif',
            batch_size=128,
            num_workers=10,
            pin_memory=True,
            label_ratio=label_ratio,
        )
        if 'ssl' in name:
            module = Module.load_from_checkpoint(CKPT)
            backbone = module.backbone
        else:
            backbone = timm.create_model(
                BACKBONE,
                pretrained=pretrained, 
                in_chans=len(BANDS), 
                features_only=True
            )
        module = EuroSATModule(
            {
                'freeze': freeze,
                'num_classes': 10,
            },
            backbone=backbone,
        )
        trainer = L.Trainer(
            max_epochs=MAX_EPOCHS,
            accelerator='gpu',
            devices=1,
            precision='bf16-mixed',
            enable_checkpointing=False,
            logger=CSVLogger(
                save_dir='logs',
                name=f'{name}-{label_ratio}',
            )
        )
        trainer.fit(module, dm)
