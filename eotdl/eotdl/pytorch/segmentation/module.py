import lightning as L
import torch
import torch.nn as nn
from torchmetrics.classification import MultilabelAccuracy

from .model import SegmentationModel
from .metrics import iou

class SegmentationModule(L.LightningModule):
    def __init__(self, num_classes=6, encoder='resnet18', in_channels=3, pretrained=True, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()
        self.model = SegmentationModel(num_classes, encoder, in_channels, pretrained)
        self.loss = nn.BCEWithLogitsLoss()

    def forward(self, x):
        return self.model(x)
    
    def predict(self, x):
        self.eval()
        with torch.no_grad():
            preds = self.model(x.to(self.device))
            return torch.argmax(preds, dim=1)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        metric = iou(y_hat, y)
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_iou', metric, prog_bar=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        metric = iou(y_hat, y)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_iou', metric, prog_bar=True)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)
 