import torch.nn as nn
import torch

from ..segmentation.model import SegmentationModel

class MultiTaskModel(SegmentationModel):
    def __init__(self, num_seg_classes=6, num_cls_classes=6, encoder='resnet18', in_channels=3, pretrained=True):
        super().__init__(num_seg_classes, encoder, in_channels, pretrained)
        self.classifier = nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(output_size=(1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(
                self.encoder.feature_info.channels(-1), num_cls_classes)
        )

    def forward(self, x):
        f = self.encoder(x)
        x = f[-1]
        for i, d in enumerate(self.decoder):
            x = d(x, f[-i-2])
        return self.conv_last(x), self.classifier(f[-1])