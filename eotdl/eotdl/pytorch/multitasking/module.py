import lightning as L
import torch
import torch.nn as nn
from torchmetrics.classification import MultilabelAccuracy

from .model import MultiTaskModel
from ..segmentation.metrics import iou
    
# train a model for classification and segmentation at the same time

class MultiTaskModule(L.LightningModule):
    def __init__(self, num_seg_classes=4, num_cls_classes=4, encoder='resnet18', in_channels=3, pretrained=True, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()
        self.model = MultiTaskModel(num_seg_classes, num_cls_classes, encoder, in_channels, pretrained)
        self.seg_loss = nn.BCEWithLogitsLoss()
        self.cls_loss = nn.BCEWithLogitsLoss()
        self.train_cls_acc = MultilabelAccuracy(num_labels=num_cls_classes)
        self.val_cls_acc = MultilabelAccuracy(num_labels=num_cls_classes)

    def forward(self, x):
        return self.model(x)
    
    def predict(self, x):
        self.eval()
        with torch.no_grad():
            seg_preds, cls_preds = self.model(x.to(self.device))
            return torch.sigmoid(seg_preds, dim=1), torch.argmax(cls_preds, dim=1)
    
    def training_step(self, batch, batch_idx):
        x, y_seg, y_cls = batch
        y_hat_seg, y_hat_cls = self(x)
        loss = self.seg_loss(y_hat_seg, y_seg) + self.cls_loss(y_hat_cls, y_cls)
        self.train_cls_acc(y_hat_cls, y_cls)
        metric = iou(y_hat_seg, y_seg)
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_acc', self.train_cls_acc, prog_bar=True, logger=True)
        self.log('train_iou', metric, prog_bar=True, logger=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y_seg, y_cls = batch
        y_hat_seg, y_hat_cls = self(x)
        loss = self.seg_loss(y_hat_seg, y_seg) + self.cls_loss(y_hat_cls, y_cls)
        self.val_cls_acc(y_hat_cls, y_cls)
        metric = iou(y_hat_seg, y_seg)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', self.val_cls_acc, prog_bar=True, logger=True)
        self.log('val_iou', metric, prog_bar=True, logger=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)