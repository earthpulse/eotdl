import torch.nn as nn
import timm
import torch.nn.functional as F
import torch

class ClassificationModel(nn.Module):
    def __init__(self, num_classes=6, encoder='resnet18', in_channels=3, pretrained=True):
        super().__init__()
        self.model = timm.create_model(encoder, pretrained=pretrained, in_chans=in_channels, num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

def conv3x3_bn(ci, co):
    return torch.nn.Sequential(
        torch.nn.Conv2d(ci, co, 3, padding=1),
        torch.nn.BatchNorm2d(co),
        torch.nn.ReLU(inplace=True)
    )

def encoder_conv(ci, co):
  return torch.nn.Sequential(
        torch.nn.MaxPool2d(2),
        conv3x3_bn(ci, co),
        conv3x3_bn(co, co),
    )

class deconv(torch.nn.Module):
    def __init__(self, ci, co):
        super(deconv, self).__init__()
        self.upsample = torch.nn.ConvTranspose2d(ci, co, 2, stride=2)
        self.conv1 = conv3x3_bn(2*co, co)
        self.conv2 = conv3x3_bn(co, co)
    
    def forward(self, x1, x2):
        x1 = self.upsample(x1)
        diffX = x2.size()[2] - x1.size()[2]
        diffY = x2.size()[3] - x1.size()[3]
        x1 = F.pad(x1, (diffX, 0, diffY, 0))
        x = torch.cat([x2, x1], dim=1)
        x = self.conv1(x)
        x = self.conv2(x)
        return x
    
class SegmentationModel(nn.Module):
    def __init__(self, num_classes=6, encoder='resnet18', in_channels=3, pretrained=True):
        super().__init__()
        self.encoder = timm.create_model(encoder, pretrained=pretrained, in_chans=in_channels, features_only=True)
        decoder_channels = self.encoder.feature_info.channels()[::-1]
        self.decoder = nn.ModuleList(
            [deconv(decoder_channels[i], decoder_channels[i+1]) for i in range(len(decoder_channels)-1)]
        )
        extra_channels = decoder_channels[-1] // 2  
        self.conv_last = nn.Sequential(
            torch.nn.ConvTranspose2d(decoder_channels[-1], extra_channels, 2, stride=2),
            conv3x3_bn(extra_channels, extra_channels),
            conv3x3_bn(extra_channels, extra_channels),
            torch.nn.Conv2d(extra_channels, num_classes, 1)
        )

    def forward(self, x):
        f = self.encoder(x)
        x = f[-1]
        for i, d in enumerate(self.decoder):
            x = d(x, f[-i-2])
        x = self.conv_last(x)
        return x
    
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