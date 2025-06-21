import lightning as L
import torch
import torch.nn as nn
from torchmetrics.classification import MultilabelAccuracy

from .model import ClassificationModel, SegmentationModel, MultiTaskModel

class ClassificationModule(L.LightningModule):
    def __init__(self, num_classes=4, encoder='resnet18', in_channels=3, pretrained=True, lr=1e-3, ssl=None):
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

def iou(pr, gt, th=0.5, eps=1e-7):
    pr = torch.sigmoid(pr) > th
    intersection = torch.sum(gt * pr, axis=(-2, -1))
    union = (
        torch.sum(gt, axis=(-2, -1)) + torch.sum(pr, axis=(-2, -1)) - intersection + eps
    )
    ious = (intersection + eps) / union
    return torch.mean(ious)

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