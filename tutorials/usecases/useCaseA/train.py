import lightning as L
from src.dm import DataModule
from src.cbs import SSLOnlineEvaluator
from src.module import Module
from lightning.pytorch.loggers import CSVLogger
from lightning.pytorch.callbacks import ModelCheckpoint
import torch

DATASET = 'sentinel2'
BATCH_SIZE = 256
MAX_EPOCHS = 200
BACKBONE = 'resnet18'
MLP_DIM = 2048
HEAD_EPOCHS = 10
EVAL_PERIOD = 10

config = {
    'satellogic': {
        'path': '/fastdata/Satellogic/data/tifs/satellogic',
        'hparams': {
            'in_chans': 4,
            'bands': (1,2,3,4)
        }
    },
    'sentinel2': {
        'path': '/fastdata/Satellogic/data/tifs/sentinel2',
        'hparams': {
            'in_chans': 4,
            'bands': (4,3,2,8)
        }
    },
    'eurosat': {
        'path': '/fastdata/EuroSAT/ds/images/remote_sensing/otherDatasets/sentinel_2/tif',
        'hparams': {
            'freeze': 'True',
            'bands': (4,3,2,8)
        }
    }
}

dm = DataModule(
    config[DATASET]['path'], 
    bands=config[DATASET]['hparams']['bands'], 
    batch_size=BATCH_SIZE
)

hparams = config[DATASET]['hparams'].copy()
hparams.update({
    'backbone': BACKBONE,
    'mlp_dim': MLP_DIM
})

module = Module(hparams)

callbacks = [
    ModelCheckpoint(
        dirpath='checkpoints',
        monitor='loss',
        mode='min',
        save_top_k=1,
        save_last=True,
        filename='{epoch}-{loss:.5f}'
    )
]
if DATASET == 'sentinel2':
    callbacks.append(
        SSLOnlineEvaluator(
            config['eurosat']['path'], 
            bands=config['eurosat']['hparams']['bands'], 
            label_ratio=0.01,
            head_epochs=HEAD_EPOCHS, 
            eval_period=EVAL_PERIOD
        )
    )


# torch.set_float32_matmul_precision('medium')
                                   
trainer=L.Trainer(
    max_epochs=MAX_EPOCHS,
    accelerator='gpu',
    devices=1,
    precision="bf16-mixed",
    logger=CSVLogger('logs', name='usecaseA'),
    callbacks=callbacks,
)

trainer.fit(module, dm)
