import lightning as L
from eotdl.pytorch.unsupervised import UnsupervisedDataModule, SSLOnlineEvaluator, UnsupervisedModule
from lightning.pytorch.loggers import CSVLogger
from lightning.pytorch.callbacks import ModelCheckpoint
import torch

DATASET = 'satellogic'
BATCH_SIZE = 256
MAX_EPOCHS = 100
BACKBONE = 'resnet18'
MLP_DIM = 2048
HEAD_EPOCHS = 10
EVAL_PERIOD = 10

config = {
    'satellogic': {
        'path': 'data/tifs/satellogic',
        'hparams': {
            'in_chans': 3,
            'bands': (1,2,3)#,4)
        }
    },
    'sentinel2': {
        'path': 'data/tifs/sentinel2',
        'hparams': {
            'in_chans': 3,
            'bands': (4,3,2)#,8)
        }
    },
    'eurosat': {
        'path': 'data/EuroSAT/ds/images/remote_sensing/otherDatasets/sentinel_2/tif',
        'hparams': {
            'freeze': 'True',
            'bands': (4,3,2)#,8)
        }
    }
}

dm = UnsupervisedDataModule(
    config[DATASET]['path'], 
    bands=config[DATASET]['hparams']['bands'], 
    batch_size=BATCH_SIZE
)

hparams = config[DATASET]['hparams'].copy()
hparams.update({
    'backbone': BACKBONE,
    'mlp_dim': MLP_DIM
})

module = UnsupervisedModule(hparams)

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
    callbacks.append(
        ModelCheckpoint(
            dirpath='checkpoints',
            monitor='eurosat_val_acc',
            mode='max',
            save_top_k=1,
            save_last=True,
            filename='eurosat-{epoch}-{eurosat_val_acc:.5f}'
        )
    )


torch.set_float32_matmul_precision('medium')
                                   
trainer=L.Trainer(
    max_epochs=MAX_EPOCHS,
    accelerator='gpu',
    devices=1,
    precision="bf16-mixed",
    logger=CSVLogger('logs', name='unsupervised'),
    callbacks=callbacks,
    limit_train_batches=1000
)

trainer.fit(module, dm)
