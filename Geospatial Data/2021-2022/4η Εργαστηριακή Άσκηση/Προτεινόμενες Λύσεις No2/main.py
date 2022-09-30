from pathlib import Path
import re
import json

import random
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import classification_report, ConfusionMatrixDisplay

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, Subset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from torchvision.io import read_video
from torchvision.models import resnet18, ResNet18_Weights
from torchvision.models.feature_extraction import create_feature_extractor

import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from torchmetrics import Accuracy

# ________________________________ LAB3 IMPORTS ________________________________


class LightningClassifier(pl.LightningModule):
    """Basic template for a LightningModule classifier."""

    def __init__(self, num_classes, ignore_index=None, mdmc_average=None):
        super().__init__()
        self.num_classes = num_classes
        self.cross_entropy = nn.CrossEntropyLoss(
            ignore_index=ignore_index if ignore_index is not None else -100
        )
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


def create_dataloaders(
    dataset_train: Optional[Dataset],
    dataset_val: Optional[Dataset],
    dataset_test: Optional[Dataset],
    batch_size,
    collate_fn=None,
    num_workers=0
):
    loader_train = DataLoader(
        dataset_train,
        shuffle=True,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    ) if dataset_train is not None else None

    loader_val = DataLoader(
        dataset_val,
        shuffle=False,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    ) if dataset_val is not None else None

    loader_test = DataLoader(
        dataset_test,
        shuffle=False,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    ) if dataset_test is not None else None

    return loader_train, loader_val, loader_test


def evaluate_predictions(
    output_dir,
    y_true,
    y_pred,
    class_names=None,
    verbose=True,
    title=None,
    figsize=(6, 6),
) -> None:
    """Compute and save a classification report and a confusion matrix."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(
            classification_report(
                y_true, y_pred, target_names=class_names, output_dict=False
            )
        )
    report = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True
    )
    with open(output_dir / 'classification_report.json', 'w') as f:
        json.dump(report, f, indent=4)

    fig, ax = plt.subplots(figsize=figsize)
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=class_names,
        xticks_rotation=90,
        ax=ax,
        colorbar=False,
    )
    ax.set_title(title)
    fig.savefig(
        output_dir / 'confusion_matrix.pdf',
        facecolor='white',
        bbox_inches='tight',
    )


def train_evaluate_lit_classifier(
    model: LightningClassifier,
    dataset_train: Dataset,
    dataset_val: Optional[Dataset],
    dataset_test: Optional[Dataset],
    *,
    max_epochs,
    batch_size,
    class_names,
    output_dir,
    ignore_index=None,
    callbacks=None,
    collate_fn=None,
    num_workers=2,
    accelerator='cpu',
) -> None:
    """Train a LightningClassifier
    and save a classification report and a confusion matrix.
    """
    if callbacks is None:
        monitor = 'loss/val' if dataset_val is not None else 'loss/train'
        callbacks = [ModelCheckpoint(monitor=monitor, mode='min')]
    assert any(isinstance(cb, ModelCheckpoint) for cb in callbacks)

    loader_train, loader_val, loader_test = create_dataloaders(
        dataset_train,
        dataset_val,
        dataset_test,
        batch_size=batch_size,
        num_workers=num_workers,
        collate_fn=collate_fn,
    )

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator=accelerator,
        callbacks=callbacks,
        default_root_dir=output_dir,
    )
    trainer.fit(
        model, train_dataloaders=loader_train, val_dataloaders=loader_val
    )

    if dataset_test is not None:
        best_model = trainer.model.load_from_checkpoint(
            trainer.checkpoint_callback.best_model_path
        )
        trainer.test(best_model, loader_test)

        # Assuming that target == batch[-1]
        y_true = [batch[-1] for batch in loader_test]
        y_true = torch.cat(y_true).view(-1)

        y_pred, _ = zip(*trainer.predict(best_model, loader_test))
        y_pred = torch.cat(y_pred).view(-1)

        if ignore_index is not None:
            keep_mask = y_true != ignore_index
            y_true = y_true[keep_mask]
            y_pred = y_pred[keep_mask]

        title = best_model.__class__.__name__
        evaluate_predictions(
            output_dir=output_dir,
            y_true=y_true,
            y_pred=y_pred,
            title=title,
            class_names=class_names,
        )


# __________________________________ DATASETS __________________________________


class Ucf101(Dataset):
    """The UCF101 dataset. Caching of the transform is supported."""

    def __init__(
        self,
        root_dir,
        mode: str,
        transform=None,
        cache_fetched=False,
        cache_exist_ok=False,
        cuda=False,
    ):
        """If isinstance(transform, nn.Module) and cuda=True,
        then multiprocessing will fail (e.g. when using a DataLoader).
        Workers might crash even when cuda=False, for reasons unknown. Thus,
        it is advised to avoid using a DataLoader if not everything is cached.
        Instead, make a call to `cache_all` first.
        """
        if mode not in {'train', 'test'}:
            raise ValueError('Invalid `mode`. Valid values: "train", "test"')

        self.root_dir = Path(root_dir)
        self.mode = mode
        self.transform = transform
        self.cache_fetched = cache_fetched

        # Create a directory to cache fetched videos, if appropriate
        if self.cache_fetched:
            self.cache_dir = self.root_dir / f'{self.__class__.__name__}_cache'
            (self.cache_dir /
             self.mode).mkdir(parents=True, exist_ok=cache_exist_ok)
        else:
            self.cache_dir = None

        # Load the video filenames, and their respective labels
        csv_path = self.root_dir / f'{self.mode}.csv'
        csv_ = np.genfromtxt(
            csv_path, delimiter=',', names=True, dtype=None, encoding=None
        )
        self.filenames = csv_['video_name']
        self.class_names, ys = np.unique(csv_['tag'], return_inverse=True)
        self.ys = torch.as_tensor(ys)

        # Move the transform to gpu, if it is a Module.
        if isinstance(self.transform, nn.Module):
            self.device = torch.device('cuda:0' if cuda else 'cpu')
            self.transform.to(self.device)
        else:
            self.device = None

    def __getitem__(self, idx):
        file_name = Path(self.filenames[idx])
        y = self.ys[idx]

        file_path = self.root_dir / self.mode / file_name

        if self.cache_fetched:
            cache_path = self.cache_dir / self.mode / file_name.with_suffix(
                '.npy'
            )
            if cache_path.exists():
                x = np.load(cache_path)
            else:
                x = self.read_transform_video(file_path)
                np.save(cache_path, x)
        else:
            x = self.read_transform_video(file_path)

        x = torch.as_tensor(x)
        return x, y

    def __len__(self):
        return len(self.filenames)

    def read_transform_video(self, file_path):
        x, *_ = read_video(str(file_path), output_format='TCHW', pts_unit='sec')
        if self.transform is not None:
            if isinstance(self.transform, nn.Module):
                x = x.to(self.device)
            x = self.transform(x).cpu()
        return x


class ResNet18ExtractorVideo(nn.Module):
    """On each video frame, apply the default transforms
    of a Resnet18 that is pretrained on ImageNet,
    and then apply the ResNet18 with its final layer removed.
    The result is a sequence of 512-dimensional vectors.
    """

    def __init__(self):
        super().__init__()
        self.weights = ResNet18_Weights.IMAGENET1K_V1
        self.preprocessor = self.weights.transforms()
        model = resnet18(weights=self.weights)
        self.extractor = create_feature_extractor(model, ['flatten'])
        self.extractor.eval()

    @torch.inference_mode()
    def forward(self, vid):
        need_squeeze = False
        if vid.ndim < 5:
            vid = vid.unsqueeze(dim=0)
            need_squeeze = True
        N, T, C, H, W = vid.shape
        vid = vid.view(-1, C, H, W)

        vid = self.preprocessor(vid)
        vid = self.extractor(vid)['flatten']

        vid = vid.view(N, T, -1)
        if need_squeeze:
            vid = vid.squeeze(dim=0)
        return vid


def cache_all(source_root_dir):
    """Iterate over the UCF01 dataset with the ResNet18ExtractorVideo transform,
    so that the entire dataset gets cached.
    Call this first to avoid errors in data loading.
    """
    cuda = torch.cuda.is_available()
    transform = ResNet18ExtractorVideo()
    dataset_train = Ucf101(
        root_dir=source_root_dir,
        mode='train',
        transform=transform,
        cache_fetched=True,
        cache_exist_ok=True,
        cuda=cuda,
    )
    dataset_test = Ucf101(
        root_dir=source_root_dir,
        mode='test',
        transform=transform,
        cache_fetched=True,
        cache_exist_ok=True,
        cuda=cuda,
    )

    for dataset in dataset_train, dataset_test:
        for _ in dataset:
            pass


def plot_transformed(video_path, nframes=10):
    vid, *_ = read_video(video_path, output_format='TCHW', pts_unit='sec')
    preprocessor = ResNet18_Weights.IMAGENET1K_V1.transforms()
    preprocessed = preprocessor(vid)

    vid = np.transpose(vid, (0, 2, 3, 1))
    preprocessed = np.transpose(preprocessed, (0, 2, 3, 1))

    fig, axs = plt.subplots(nrows=nframes, ncols=2, figsize=(8, 16))
    fig.set_tight_layout(True)
    for i in range(nframes):
        axs[i, 0].imshow(vid[i])
        axs[i, 1].imshow(preprocessed[i])
        axs[i, 0].set_axis_off()
        axs[i, 1].set_axis_off()


def train_val_split(dataset_train_original, n_groups_val, seed=None):
    """Splits train UCF101 dataset into train and validation datasets.
    
    Every class in the train UCF101 directory has 18 video groups,
    and every video group has roughly the same amount of videos,
    which are cuts of a single original video.
    A random selection of `n_groups_val` video groups of each class
    will comprise our validation set,
    and the remaining `18 - n_groups_val` video groups
    will comprise our validation set.
    
    More specific statistics about the dataset can be found below.
    
    >>> import pandas as pd
    >>> video_names = pd.read_csv('data/train.csv')['video_name']
    >>> pattern = r'v_(?P<label>[a-zA-Z]*)_g(?P<group>\d+)_c(?P<cut>\d+)'
    >>> df = video_names.str.extract(pattern)
    >>> df = df.astype({'group': int, 'cut': int})
    >>> df = df.sort_values(by=['label', 'group', 'cut'])
    >>> df.groupby(['label', 'group'])['cut'].count().value_counts()
    7    64
    6    19
    5     4
    4     3
    Name: cut, dtype: int64
    >>> df.groupby('label')['group'].agg(['min', 'max', 'nunique', 'count'])
                  min  max  nunique  count
    label
    CricketShot     8   25       18    118
    PlayingCello    8   25       18    120
    Punch           8   25       18    121
    ShavingBeard    8   25       18    118
    TennisSwing     8   25       18    117
    """

    if seed is not None:
        random.seed(seed)
    val_video_groups = set(random.sample(range(8, 26), n_groups_val))
    print(f'Making validation set from video groups {sorted(val_video_groups)}')
    p = re.compile(r'v_[a-zA-Z]*_g(\d+)_')
    train_indices, val_indices = [], []

    for i, s in enumerate(dataset_train_original.filenames):
        video_group = int(p.match(s).group(1))
        if video_group in val_video_groups:
            val_indices.append(i)
        else:
            train_indices.append(i)

    dataset_train = Subset(dataset_train_original, train_indices)
    dataset_val = Subset(dataset_train_original, val_indices)

    return dataset_train, dataset_val


def rnn_collate_fn(batch):
    seqs, y = map(list, zip(*batch))
    padded = pad_sequence(seqs, batch_first=True)
    y = torch.stack(y)
    return padded, y


def transformer_collate_fn(batch):
    seqs, y = map(list, zip(*batch))
    src = pad_sequence(seqs, batch_first=True)
    lengths = torch.asarray(list(map(len, seqs)))
    src_key_padding_mask = torch.arange(lengths.max()) >= lengths[..., None]
    y = torch.stack(y)
    return src, src_key_padding_mask, y


# ___________________________________ MODELS ___________________________________


class GRUClassifier(LightningClassifier):
    """A sequence to vector GRU with a final linear layer for classification."""

    def __init__(
        self,
        input_size,
        rnn_size,
        num_classes,
        num_rnn_layers,
        dropout=0.1,
        lr=1e-3,
    ):
        super().__init__(num_classes)
        self.save_hyperparameters()

        self.dropout = dropout
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=rnn_size,
            num_layers=num_rnn_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.linear = nn.Linear(rnn_size, self.num_classes)
        self.lr = lr

    def forward(self, x):
        x, _ = self.gru(x)
        x = x[:, -1, :]
        x = F.dropout(x, self.dropout)
        x = self.linear(x)
        return x

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer


class PositionalEncoder(nn.Module):
    """Positional encoding as implemented in "Attention is all you need"."""

    def __init__(self, d_model, max_len):
        super().__init__()

        pos = torch.arange(max_len).unsqueeze(1)
        exponents = torch.arange(0, d_model, 2) / (-d_model)
        angle_rates = torch.pow(10_000.0, exponents)
        angles = pos * angle_rates
        encoding = torch.empty(1, max_len, d_model)
        encoding[0, :, 0::2] = torch.sin(angles)
        encoding[0, :, 1::2] = torch.cos(angles)

        self.register_buffer('encoding', encoding)

    def forward(self, x):
        x = x + self.encoding[:, :x.shape[1], :]
        return x


class TransformerClassifier(LightningClassifier):
    """Transformer encoder with a maxpooling layer over the encoded outputs,
    and a final linear layer for classification."""

    def __init__(
        self,
        d_model,
        nhead,
        dim_feedforward,
        num_layers,
        num_classes,
        dropout=0.1,
        max_len=1_000,
        lr=1e-3,
    ):
        super().__init__(num_classes)
        self.save_hyperparameters()

        self.dropout = dropout
        self.positional_encoder = PositionalEncoder(d_model, max_len=max_len)
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer=nn.TransformerEncoderLayer(
                d_model,
                nhead,
                dim_feedforward,
                dropout=dropout,
                batch_first=True,
            ),
            num_layers=num_layers,
        )
        self.linear = nn.Linear(d_model, self.num_classes)
        self.lr = lr

    def forward(self, src, mask=None, src_key_padding_mask=None):
        # src.shape = B, T, D
        x = self.positional_encoder(src)
        x = F.dropout(x, p=self.dropout)
        x = self.transformer_encoder(
            x, mask=mask, src_key_padding_mask=src_key_padding_mask
        )
        x = torch.amax(x, 1)  # B, D
        x = F.dropout(x, p=self.dropout)
        x = self.linear(x)  # B, C
        return x

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer

    def get_logits_and_target(self, batch):
        x, src_key_padding_mask, y = batch
        logits = self(x, src_key_padding_mask=src_key_padding_mask)
        return logits, y


# __________________________________ TRAINING __________________________________


def main():
    pl.utilities.seed.seed_everything(42)
    data_root_dir = 'data'
    cache_all(data_root_dir)
    transform = None  # Hack to save some memory. Requires cache_all(root_dir).

    dataset_train_original = Ucf101(
        root_dir=data_root_dir,
        mode='train',
        transform=transform,
        cache_fetched=True,
        cache_exist_ok=True,
    )  # 594 samples
    dataset_train, dataset_val = train_val_split(
        dataset_train_original, 3
    )  # ~(15/18, 3/18) * 594 = (495, 99) samples
    dataset_test = Ucf101(
        root_dir=data_root_dir,
        mode='test',
        transform=transform,
        cache_fetched=True,
        cache_exist_ok=True,
    )  # 224 samples
    print(f'Train samples: {len(dataset_train)}')
    print(f'Validation samples {len(dataset_val)}')
    print(f'Test samples: {len(dataset_test)}\n')

    class_names = dataset_train_original.class_names
    accelerator = 'gpu' if torch.cuda.is_available() else 'cpu'

    # RNN
    train_evaluate_lit_classifier(
        GRUClassifier(
            input_size=512,
            rnn_size=512,
            num_classes=5,
            num_rnn_layers=2,
            lr=1e-3,
        ),
        dataset_train,
        dataset_val,
        dataset_test,
        class_names=class_names,
        collate_fn=rnn_collate_fn,
        max_epochs=300,
        batch_size=32,
        output_dir='output/rnn',
        accelerator=accelerator,
        callbacks=[
            EarlyStopping(monitor='loss/val', mode='min', patience=50),
            ModelCheckpoint(monitor='loss/val', mode='min'),
        ],
    )
    # Transformer
    train_evaluate_lit_classifier(
        TransformerClassifier(
            d_model=512,
            nhead=8,
            dim_feedforward=2048,
            num_layers=2,
            num_classes=5,
            lr=1e-3,
        ),
        dataset_train,
        dataset_val,
        dataset_test,
        class_names=class_names,
        collate_fn=transformer_collate_fn,
        max_epochs=300,
        batch_size=32,
        output_dir='output/transformer',
        accelerator=accelerator,
        callbacks=[
            EarlyStopping(monitor='loss/val', mode='min', patience=50),
            ModelCheckpoint(monitor='loss/val', mode='min'),
        ],
    )


if __name__ == '__main__':
    main()
