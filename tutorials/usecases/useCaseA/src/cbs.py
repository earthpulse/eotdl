# src/cbs/ssl_online_evaluator.py

import torch
from lightning.pytorch.callbacks import Callback
from tqdm.auto import tqdm
from .dm import EuroSATDataModule


class SSLOnlineEvaluator(Callback):
    """
    Every `eval_period` epochs, freeze the backbone, train a small linear head
    (for `head_epochs` epochs) on EuroSAT's train split, then evaluate on EuroSAT's
    val split and log accuracy. Additionally, run once before training epoch 1.

    Args:
        path (str): where EuroSAT lives on disk
        bands (tuple): which bands to load, e.g. (4,3,2,8)
        eval_period (int): run linear-eval every `eval_period` epochs
        head_epochs (int): how many epochs to train the linear head each time
        num_classes (int): number of classes (EuroSAT is 10)
        lr (float): learning rate for the linear head
    """

    def __init__(
        self,
        path: str,
        bands: tuple = (4, 3, 2, 8),
        label_ratio: float = 0.01,
        eval_period: int = 10,
        head_epochs: int = 10,
        num_classes: int = 10,
        lr: float = 1e-3,
    ):
        super().__init__()
        self.eval_period = eval_period
        self.head_epochs = head_epochs
        self.num_classes = num_classes
        self.lr = lr
        self.label_ratio = label_ratio

        # Our EuroSAT DataModule (for the "linear eval" part)
        self.dm = EuroSATDataModule(path=path, bands=bands, label_ratio=self.label_ratio)

        # placeholders; set in on_train_start
        self.head: torch.nn.Module = None
        self.optimizer: torch.optim.Optimizer = None
        self.criterion = torch.nn.CrossEntropyLoss()
        self.feat_dim: int = None

    def on_train_start(self, trainer, pl_module):
        """
        Called once, before the very first training epoch (epoch 0) begins.
        We:
          1) call dm.setup()
          2) do a quick forward pass to infer feature dims → build self.head + self.optimizer
          3) run the linear-evaluation right away (helper method)
        """
        # ─── 1) prepare EuroSAT splits ─────────────────────────────────
        self.dm.setup(stage="fit")

        # ─── 2) build the linear head ──────────────────────────────────
        # grab one batch just to infer "C" from the backbone's output
        train_loader = self.dm.train_dataloader()
        inputs, _ = next(iter(train_loader))
        inputs = inputs.to(pl_module.device)

        backbone = pl_module.backbone
        backbone.eval()
        with torch.no_grad():
            feats = backbone(inputs)
            if isinstance(feats, (list, tuple)):
                feats = feats[-1]
        self.feat_dim = feats.shape[1] # Store feat_dim

        # Remove head and optimizer initialization from here
        # self.head = torch.nn.Sequential(
        #     torch.nn.AdaptiveAvgPool2d((1, 1)),
        #     torch.nn.Flatten(),
        #     torch.nn.Linear(feat_dim, self.num_classes),
        # ).to(pl_module.device)

        # self.optimizer = torch.optim.Adam(self.head.parameters(), lr=self.lr)

        # return the backbone to train mode (so your main unsupervised loss still updates it)
        backbone.train()

        # ─── 3) run a first evaluation "before epoch 1" ────────────────
        # By calling our helper method here, we get a "first peek" at
        # `"eurosat_val_acc"` right away, before any training epoch runs.
        self._run_linear_eval(trainer, pl_module)

    def on_train_epoch_end(self, trainer, pl_module, outputs=None):
        """
        Called after each training epoch. If (epoch+1) % eval_period == 0,
        do another linear evaluation.
        """
        epoch = trainer.current_epoch
        # keep the same periodic check:
        if (epoch + 1) % self.eval_period != 0:
            return

        self._run_linear_eval(trainer, pl_module)

    def _run_linear_eval(self, trainer, pl_module):
        """
        Helper that:
          1) freezes the backbone
          2) trains self.head for head_epochs on EuroSAT train split (with a tqdm bar)
          3) evaluates self.head on EuroSAT val split (computes accuracy)
          4) logs "eurosat_val_acc" via pl_module.log(...)
          5) unfreezes the backbone
        """
        backbone = pl_module.backbone
        device = pl_module.device

        # Re-initialize head and optimizer here to train from scratch
        self.head = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(self.feat_dim, self.num_classes),
        ).to(device)
        self.optimizer = torch.optim.Adam(self.head.parameters(), lr=self.lr)

        # ─── 1) freeze backbone ───────────────────────────────────────
        backbone.eval()
        for p in backbone.parameters():
            p.requires_grad = False

        # ─── 2) train the head for head_epochs, showing a tqdm bar ────
        self.head.train()
        # print(f"Training head for {self.head_epochs} epochs...", end="", flush=True)
        for head_epoch in range(self.head_epochs):
            # loop = tqdm(
            #     self.dm.train_dataloader(),
            #     desc=f"[Head {head_epoch+1}/{self.head_epochs}]",
            #     leave=False,
            # )
            # for inputs, targets in loop:
            for inputs, targets in self.dm.train_dataloader():
                inputs = inputs.to(pl_module.device)
                targets = targets.to(pl_module.device)

                with torch.no_grad():
                    feats = backbone(inputs)
                    if isinstance(feats, (list, tuple)):
                        feats = feats[-1]
                feats = feats.detach()

                logits = self.head(feats)
                loss = self.criterion(logits, targets)

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                # loop.set_postfix(loss=loss.item())

        # ─── 3) evaluate the head on EuroSAT validation ───────────────
        self.head.eval()
        correct = 0
        total = 0
        for inputs, targets in self.dm.val_dataloader():
            inputs = inputs.to(pl_module.device)
            targets = targets.to(pl_module.device)

            with torch.no_grad():
                feats = backbone(inputs)
                if isinstance(feats, (list, tuple)):
                    feats = feats[-1]
            feats = feats.detach()
            logits = self.head(feats)
            preds = torch.argmax(logits, dim=1)

            correct += (preds == targets).sum().item()
            total += targets.size(0)

        val_acc = correct / total

        # ─── 4) log accuracy to Lightning's logger & progress bar ────
        #   - on_epoch=True ensures it shows up in the epoch-level metrics
        #   - prog_bar=True makes it appear in the tqdm bar
        pl_module.log(
            "eurosat_val_acc",
            val_acc,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
        )

        # ─── 5) unfreeze backbone ─────────────────────────────────────
        backbone.train()
        for p in backbone.parameters():
            p.requires_grad = True
