import lightning as L
import segmentation_models_pytorch as smp
import torch
import timm

class Module(L.LightningModule):

    def __init__(self, config):
        super().__init__()
        self.save_hyperparameters(config)
        self.backbone = timm.create_model(
            self.hparams.backbone,
            pretrained=False,
            features_only=True,
            in_chans=self.hparams.in_chans
        )
        self.head = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(
                self.backbone.feature_info.channels(-1), self.hparams.mlp_dim),
            torch.nn.BatchNorm1d(self.hparams.mlp_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.hparams.mlp_dim, self.hparams.mlp_dim),
            torch.nn.BatchNorm1d(self.hparams.mlp_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(self.hparams.mlp_dim, self.hparams.mlp_dim)
        )
        self.l = 5e-3

    def forward(self, x):
        return self.head(self.backbone(x)[-1])

    def training_step(self, batch, batch_idx):
        # two randomly augmented versions of x
        x1, x2 = batch
        # compute representations
        z1 = self(x1)
        z2 = self(x2)
        # normalize repr. along the batch dimension
        N, D = z1.shape
        z1_norm = (z1 - z1.mean(0)) / z1.std(0)  # NxD
        z2_norm = (z2 - z2.mean(0)) / z2.std(0)  # NxD
        # cross-correlation matrix
        c = (z1_norm.T @ z2_norm) / N  # DxD
        # loss
        c_diff = (c - torch.eye(D, device=self.device)).pow(2)  # DxD
        # multiply off-diagonal elems of c_diff by lambda
        d = torch.eye(D, dtype=bool)
        c_diff[~d] *= self.l
        loss = c_diff.sum()
        self.log('loss', loss, prog_bar=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters())
        max_epochs = self.trainer.max_epochs
        scheduler = torch.optim.lr_scheduler.MultiStepLR(
            optimizer, milestones=[int(0.6*max_epochs), int(0.8*max_epochs)])
        return [optimizer], [scheduler]

class EuroSATModule(L.LightningModule):

    def __init__(self, config, backbone):
        super().__init__()
        self.save_hyperparameters(config)
        self.backbone = backbone
        if self.hparams.freeze:
            for param in self.backbone.parameters():
                param.requires_grad = False
        self.head = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(
                self.backbone.feature_info.channels(-1), self.hparams.num_classes)
        )
        self.criterion = torch.nn.CrossEntropyLoss()

    def forward(self, x):
        if self.hparams.freeze:
            self.backbone.eval()
            with torch.no_grad():
                features = self.backbone(x)
        else:
            features = self.backbone(x)
        return self.head(features[-1])

    def training_step(self, batch, batch_idx):
        loss, acc = self.shared_step(batch)
        self.log('loss', loss)
        self.log('acc', acc, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        loss, acc = self.shared_step(batch)
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', acc, prog_bar=True)

    def shared_step(self, batch):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        acc = (torch.argmax(logits, axis=1) == y).sum().item() / y.size(0)
        return loss, acc

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters())
