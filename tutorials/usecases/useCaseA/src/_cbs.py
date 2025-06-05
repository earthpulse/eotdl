from pytorch_lightning import Callback
from .dm import EuroSATDataModule
import torch


class SSLOnlineEvaluator(Callback):

    def __init__(self, path, bands=(4,3,2,8), max_epochs=10, check_val_every_n_epoch=1, num_classes=10):
        super().__init__()
        self.max_epochs = max_epochs
        self.check_val_every_n_epoch = check_val_every_n_epoch
        self.num_classes = num_classes
        self.dm = EuroSATDataModule(path, bands)
        self.dm.setup()
        self.criterion = torch.nn.CrossEntropyLoss()

    def on_pretrain_routine_start(self, trainer, pl_module):
        self.head = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(
                pl_module.backbone.feature_info.channels(-1), self.num_classes)
        ).to(pl_module.device)
        self.optimizer = torch.optim.Adam(self.head.parameters(), lr=1e-3)

    def on_epoch_end(self, trainer, pl_module):
        if (trainer.current_epoch + 1) % self.check_val_every_n_epoch != 0:
            return
        backbone = pl_module.backbone.eval()
        for param in backbone.parameters():
            param.requires_grad = False
        self.head.train()
        for _ in range(self.max_epochs):
            for inputs, targets in self.dm.train_dataloader():
                inputs = inputs.to(pl_module.device)
                targets = targets.to(pl_module.device)
                with torch.no_grad():
                    features = backbone(inputs)[-1]
                features = features.detach()
                logits = self.head(features)
                loss = self.criterion(logits, targets)
                loss.backward()
                self.optimizer.step()
                self.optimizer.zero_grad()
        self.head.eval()
        accuracies = []
        for inputs, targets in self.dm.val_dataloader():
            inputs = inputs.to(pl_module.device)
            with torch.no_grad():
                features = backbone(inputs)[-1]
            features = features.detach()
            logits = self.head(features)
            preds = torch.argmax(logits, dim=1).detach().cpu()
            acc = (preds == targets).sum().item() / targets.size(0)
            accuracies.append(acc)
        acc = torch.mean(torch.tensor(accuracies))
        metrics = {'eurosat_val_acc': acc}
        trainer.logger_connector.log_metrics(metrics, {})
        trainer.logger_connector.add_progress_bar_metrics(metrics)
        pl_module.backbone.train()
        for param in pl_module.backbone.parameters():
            param.requires_grad = True
