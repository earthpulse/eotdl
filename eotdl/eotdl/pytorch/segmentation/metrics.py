import torch


def iou(pr, gt, th=0.5, eps=1e-7):
    pr = torch.sigmoid(pr) > th
    intersection = torch.sum(gt * pr, axis=(-2, -1))
    union = (
        torch.sum(gt, axis=(-2, -1)) + torch.sum(pr, axis=(-2, -1)) - intersection + eps
    )
    ious = (intersection + eps) / union
    return torch.mean(ious)