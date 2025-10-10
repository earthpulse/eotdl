import lightning as L
import torch
import torch.nn as nn
from torchmetrics.classification import MultilabelAccuracy

from .model import ClassificationModel

class MultiLabelClassificationModule(L.LightningModule):
    def __init__(self, num_classes, encoder='resnet18', in_channels=3, pretrained=True, lr=1e-3, ssl=None):
        super().__init__()
        self.save_hyperparameters()
        self.model = ClassificationModel(num_classes, encoder, in_channels, pretrained, ssl)
        self.loss = nn.BCEWithLogitsLoss()
        self.train_acc = MultilabelAccuracy(num_labels=num_classes)
        self.val_acc = MultilabelAccuracy(num_labels=num_classes)

    def forward(self, x):
        return self.model(x)
    
    def predict(self, x):
        self.eval()
        with torch.no_grad():
            preds = self.model(x.to(self.device))
            return torch.sigmoid(preds, dim=1)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        self.train_acc(y_hat, y)
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_acc', self.train_acc, prog_bar=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss(y_hat, y)
        self.val_acc(y_hat, y)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', self.val_acc, prog_bar=True)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)

