import torch.nn as nn
import timm
import torch

class ClassificationModel(nn.Module):
    def __init__(self, num_classes=6, encoder='resnet18', in_channels=3, pretrained=True, ssl=None):
        super().__init__()
        self.model = timm.create_model(encoder, pretrained=pretrained, in_chans=in_channels, num_classes=num_classes)
        if ssl:
            print(f'Loading SSL checkpoint from {ssl}')
            # Load SSL checkpoint
            checkpoint = torch.load(ssl, map_location='cpu')
            state_dict = checkpoint['state_dict']
            # Remove module prefix if present (from DataParallel/DistributedDataParallel)
            new_state_dict = {}
            for k, v in state_dict.items():
                if k.startswith('module.'):
                    k = k[7:]  # remove 'module.' prefix
                new_state_dict[k] = v
            # Load the state dict
            self.model.load_state_dict(new_state_dict, strict=False)

    def forward(self, x):
        return self.model(x)

