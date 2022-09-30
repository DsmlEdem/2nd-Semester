import itertools

import torch
from torch import nn
import torch.nn.functional as F
from torchvision.models import resnet18
import pytorch_lightning as pl
from torchmetrics import Accuracy


class LightningClassifier(pl.LightningModule):
    """Basic template for a LightningModule classifier."""

    def __init__(self, num_classes, ignore_index=None, mdmc_average=None):
        super().__init__()
        self.num_classes = num_classes
        self.cross_entropy = nn.CrossEntropyLoss(
            ignore_index=ignore_index if ignore_index is not None else -100
        )
        # TODO: When ignore_index is not None the results seem incorrect.
        self.train_accuracy = Accuracy(
            num_classes=num_classes,
            ignore_index=ignore_index,
            mdmc_average=mdmc_average,
        )
        self.val_accuracy = Accuracy(
            num_classes=num_classes,
            ignore_index=ignore_index,
            mdmc_average=mdmc_average,
        )
        self.test_accuracy = Accuracy(
            num_classes=num_classes,
            ignore_index=ignore_index,
            mdmc_average=mdmc_average,
        )

    def get_logits_and_target(self, batch):
        x, *y = batch  # using * in case there is no target
        y = y[0] if y else None
        logits = self(x)
        return logits, y

    def training_step(self, batch, batch_idx, optimizer_idx=None):
        logits, y = self.get_logits_and_target(batch)
        loss = self.cross_entropy(logits, y)
        self.train_accuracy(logits, y)
        self.log_dict(
            {
                'loss/train': loss,
                'accuracy/train': self.train_accuracy
            }
        )
        return loss

    def validation_step(self, batch, batch_idx):
        logits, y = self.get_logits_and_target(batch)
        loss = self.cross_entropy(logits, y)
        self.val_accuracy(logits, y)
        self.log_dict({'loss/val': loss, 'accuracy/val': self.val_accuracy})

    def test_step(self, batch, batch_idx):
        logits, y = self.get_logits_and_target(batch)
        loss = self.cross_entropy(logits, y)
        self.test_accuracy(logits, y)
        self.log_dict({'loss/test': loss, 'accuracy/test': self.test_accuracy})

    def predict_step(self, batch, batch_idx):
        logits, _ = self.get_logits_and_target(batch)
        preds = torch.argmax(logits, dim=1)
        probs = F.softmax(logits, dim=1)
        return preds, probs


class MLPClassifier(LightningClassifier):
    """Simple 4-layer MLP with Dropout and L2 normalization"""

    def __init__(
        self, dim_in, num_classes, lr=1e-3, weight_decay=0, p_dropout=0.2
    ):
        super().__init__(num_classes)
        self.save_hyperparameters()

        self.model = nn.Sequential(
            nn.Linear(dim_in, 128),
            nn.Dropout(p_dropout),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.Dropout(p_dropout),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )
        self.lr = lr
        self.weight_decay = weight_decay

    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(
            self.parameters(), lr=self.lr, weight_decay=self.weight_decay
        )
        return optimizer


# CNN Construction
class CNNBlock(nn.Module):

    def __init__(self, channels, kernel_size=3, stride=1, padding='same'):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size, stride, padding),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size, stride, padding),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.model(x)


class CNNClassifier(LightningClassifier):
    """Deep CNN with skip connections between convolutions that are two steps away.
    Expects a 15 by 15 image.
    """

    def __init__(self, channels_in, num_classes, lr=1e-3):
        super().__init__(num_classes)
        self.save_hyperparameters()
        self.lr = lr

        self.stem = nn.Sequential(
            nn.Conv2d(channels_in, 32, kernel_size=3, stride=1, padding='same'),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding='same'),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )
        self.block1 = CNNBlock(64)
        self.block2 = CNNBlock(64)
        self.block3 = CNNBlock(64)

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(3 * 3 * 64, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.stem(x)
        x = x + self.block1(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = x + self.block2(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = x + self.block3(x)
        x = self.classifier(x)
        return x

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer


# U-Net Construction
class ConvBlock(nn.Module):

    def __init__(self, in_channels, out_channels, kernel_size=3):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                padding='same',
                bias=False,
            ), nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True),
            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size,
                padding='same',
                bias=False,
            ), nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.model(x)


class DownBlock(nn.Module):

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.model = nn.Sequential(
            nn.MaxPool2d(2), ConvBlock(in_channels, out_channels)
        )

    def forward(self, x):
        return self.model(x)


class UpBlock(nn.Module):

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.convt = nn.ConvTranspose2d(in_channels, out_channels, 2, 2)
        self.conv = ConvBlock(
            in_channels, out_channels
        )  # in_channels because of concat

    def forward(self, x, x_res):
        x = self.convt(x)
        dh = x_res.shape[-2] - x.shape[-2]
        dw = x_res.shape[-1] - x.shape[-1]
        assert dh >= 0 and dw >= 0
        padding = dh // 2, dh - dh // 2, dw // 2, dw - dw // 2
        x = F.pad(x, padding)
        x_cat = torch.cat((x, x_res), -3)
        return self.conv(x_cat)


class UNetClassifier(LightningClassifier):
    """Simple UNet implementation of depth 4"""

    def __init__(self, n_channels, num_classes, ignore_index=None, lr=1e-4):
        super().__init__(
            num_classes, ignore_index=ignore_index, mdmc_average='global'
        )
        self.save_hyperparameters()
        self.lr = lr

        self.entrance = ConvBlock(n_channels, 64)
        self.down1 = DownBlock(64, 128)
        self.down2 = DownBlock(128, 256)
        self.down3 = DownBlock(256, 512)
        self.down4 = DownBlock(512, 1024)
        self.up1 = UpBlock(1024, 512)
        self.up2 = UpBlock(512, 256)
        self.up3 = UpBlock(256, 128)
        self.up4 = UpBlock(128, 64)
        self.exit = nn.Conv2d(64, num_classes, 1)

    def forward(self, x):
        a1 = self.entrance(x)
        a2 = self.down1(a1)
        a3 = self.down2(a2)
        a4 = self.down3(a3)
        t = self.down4(a4)
        b1 = self.up1(t, a4)
        b2 = self.up2(b1, a3)
        b3 = self.up3(b2, a2)
        b4 = self.up4(b3, a1)
        logits = self.exit(b4)
        return logits

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer


class TransferResNetClassifier(LightningClassifier):
    """ResNet with the last layer replaced so that its output matches n_classes"""

    def __init__(self, num_classes, freeze_head=False, lr=1e-3):
        super().__init__(num_classes)
        self.save_hyperparameters()

        self.model = resnet18(pretrained=True)
        self.freeze_head = freeze_head
        if self.freeze_head:
            for param in self.model.parameters():
                param.requires_grad = False

        self.model.fc = nn.Linear(512, num_classes)

        self.lr = lr

    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        children = list(self.model.children())

        tail_params = children[-1].parameters()
        tail_optim = torch.optim.Adam(tail_params, lr=self.lr)

        if self.freeze_head:
            return tail_optim
        else:
            head_params = itertools.chain.from_iterable(
                child.parameters() for child in children[:-1]
            )
            head_optim = torch.optim.Adam(head_params, lr=self.lr / 200)
            return head_optim, tail_optim