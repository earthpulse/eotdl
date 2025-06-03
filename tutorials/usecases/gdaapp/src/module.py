import lightning as L
import segmentation_models_pytorch as smp
import torch

def iou(pr, gt, th=0.5, eps=1e-7):
    pr = torch.sigmoid(pr) > th
    intersection = torch.sum(gt * pr, axis=(-2, -1))
    union = (
        torch.sum(gt, axis=(-2, -1)) + torch.sum(pr, axis=(-2, -1)) - intersection + eps
    )
    ious = (intersection + eps) / union
    return torch.mean(ious)

class Module(L.LightningModule):
    def __init__(self, in_channels=3, encoder="resnet34", pretrained=True, lr=1e-3):
        super().__init__()
        self.save_hyperparameters()
        self.model = smp.Unet(
            encoder_name=encoder,
            encoder_weights='imagenet' if pretrained else None,
            in_channels=in_channels,
            classes=1,
        )
        self.loss_fn = torch.nn.BCEWithLogitsLoss()

    def forward(self, x):
        return self.model(x)
    
    def predict(self, x, threshold=0.5):
        self.eval()
        with torch.no_grad():
            y_hat = self(x.to(self.device))
        return (torch.sigmoid(y_hat) > threshold).float()
    
    def shared_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        metric = iou(y_hat, y)
        return loss, metric
    
    def training_step(self, batch, batch_idx):
        loss, metric = self.shared_step(batch, batch_idx)
        self.log('train_loss', loss, prog_bar=True)
        self.log('train_iou', metric, prog_bar=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        loss, metric = self.shared_step(batch, batch_idx)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_iou', metric, prog_bar=True)
    
    def test_step(self, batch, batch_idx):
        loss, metric = self.shared_step(batch, batch_idx)
        self.log('test_loss', loss, prog_bar=True)
        self.log('test_iou', metric, prog_bar=True)
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.lr)