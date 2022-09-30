# %%
import re
from typing import List, Optional, Tuple
from operator import itemgetter
from typing import Dict, List
from pathlib import Path
import csv
import json

from .datasets import PatchDatasetPostPad, CroppedDataset
from .models import LightningClassifier, UNetClassifier, CNNClassifier

import numpy as np
import rasterio
import matplotlib as mpl
import matplotlib.pyplot as plt

from sklearn.metrics import ConfusionMatrixDisplay, classification_report
from sklearn.pipeline import Pipeline

import torch
from torch.utils.data import DataLoader, Dataset
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

# _________________________________INPUT/OUTPUT_________________________________


def load_image(src_path) -> np.ndarray:
    with rasterio.open(src_path) as src:
        image = src.read()
    # Map integers to floats in [0, 1]
    max_val = np.iinfo(image.dtype).max
    image = image.astype(np.float32) / max_val
    return image


def load_label(src_path) -> np.array:
    with rasterio.open(src_path) as src:
        label = src.read(1)
    # 0 is the unknown class, so we remap it to -1
    # 0, 1, ... , k, --> -1, 0, ..., k-1
    label = label.astype(np.int64) - 1
    return label


def read_data(image_paths,
              label_paths) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Loads the images and labels in two separate lists."""
    images = []
    labels = []
    for x_path, y_path in zip(image_paths, label_paths):
        x_img = load_image(x_path)
        y_img = load_label(y_path)
        images.append(x_img)
        labels.append(y_img)
    return images, labels


def read_info(path) -> Dict[str, List]:
    """Read class colors and names"""
    with open(path) as f:
        reader = csv.DictReader(f)
        info = {field: [] for field in reader.fieldnames}
        for record in reader:
            for name in reader.fieldnames:
                info[name].append(record[name])
    return info


# ________________________________MODEL TRAINING________________________________


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
    figsize=(9, 9),
) -> None:
    """Compute and save a classification report and a confusion matrix"""
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
        output_dir / 'confusion_matrix.png',
        facecolor='white',
        bbox_inches='tight',
    )


def train_evaluate_sklearn_classifier(
    model, x_train, x_test, y_train, y_test, class_names, output_dir
) -> None:
    """Train a scikit-learn classifier and save a classification report and a confusion matrix"""
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    title = model.steps[-1][0] if isinstance(
        model, Pipeline
    ) else model.__class__.__name__
    evaluate_predictions(
        output_dir=output_dir,
        y_true=y_test,
        y_pred=y_pred,
        title=title,
        class_names=class_names,
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
    """Train a LightningClassifier and save a classification report and a confusion matrix"""
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


# ___________________________________PLOTTING___________________________________


def display_image_and_label(
    image,
    label,
    cmap,
    norm,
    class_names,
    rgb,
    title=None,
    axs=None,
):
    if axs is None:
        fig, axs = plt.subplots(nrows=2, figsize=(16, 6))
    image = image[rgb, ...].transpose(1, 2, 0)
    image = image / image.max()
    axs[0].imshow(image)
    axs[1].imshow(label, cmap=cmap, norm=norm)
    axs[0].set_axis_off()
    axs[1].set_axis_off()

    cbar = plt.gcf().colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=axs,
        shrink=0.9,
        location='right',
    )
    cbar.set_ticks(np.arange(cmap.N) - 0.5)
    cbar.set_ticklabels(class_names)
    plt.suptitle(title)

    return axs


def display_patch(dataset, idx, rgb, n_repeats=1, axs=None):

    def get_patch():
        patch, _ = dataset[idx]
        img = patch[rgb, ...]
        img = np.transpose(img, (1, 2, 0))
        img = img / 0.35
        return img

    if axs is None:
        fig, axs = plt.subplots(nrows=n_repeats, figsize=(2, n_repeats))

    if n_repeats == 1:
        axs.imshow(get_patch())
        axs.set_axis_off()
    else:
        for ax in axs:
            ax.imshow(get_patch())
            ax.set_axis_off()

    return axs


def display_segmentation(
    dataset, idx, cmap, norm, class_names, rgb, n_repeats=1, axs=None
):
    """Plot an item of an Augmented CroppedDataset multiple times"""

    def get_crop():
        img, label = dataset[idx]
        img = img[rgb, ...]
        img = np.transpose(img, (1, 2, 0))
        img = img / 0.35
        return img, label

    if axs is None:
        fig, axgrid = plt.subplots(
            nrows=n_repeats, ncols=2, figsize=(4, n_repeats)
        )

    for ax1, ax2 in axgrid:
        img, label = get_crop()
        ax1.imshow(img)
        ax2.imshow(label, cmap=cmap, norm=norm)
        ax1.set_axis_off()
        ax2.set_axis_off()

    cbar = plt.gcf().colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=axgrid,
        shrink=0.9,
        location='right',
    )
    cbar.set_ticks(np.arange(cmap.N) - 0.5)
    cbar.set_ticklabels(class_names)

    return axgrid


def test_cropped_dataset(src_path, use_padding, size, stride, skip_rate, rgb):
    import matplotlib.pyplot as plt
    from .utils import load_image

    # Load from disk
    src_path = Path(src_path)
    dst_path = Path('.') / f'{src_path.stem}_reconstructed.tif'
    with rasterio.open(src_path) as src:
        image = src.read()

    dataset = CroppedDataset(image, None, size, stride, use_padding=use_padding)
    loader = DataLoader(dataset)

    # Write to disk
    with rasterio.open(
        dst_path,
        'w',
        height=dataset.image.shape[-2],
        width=dataset.image.shape[-1],
        count=dataset.image.shape[0],
        dtype=dataset.image.dtype,
        driver='Gtiff',
    ) as dst:
        for idx, x in enumerate(loader):
            if idx % skip_rate == 0:
                continue
            min_i, min_j, max_i, max_j = dataset.get_bounds(idx)
            window = rasterio.windows.Window.from_slices(
                (min_i, max_i), (min_j, max_j)
            )
            dst.write(x[0][0], window=window)

    fig, axs = plt.subplots(nrows=2, figsize=(16, 9))

    image = dataset.image[rgb, ...].transpose(1, 2, 0)
    image = image / image.max()
    axs[0].imshow(image)
    axs[0].set_axis_off()
    del image

    recon = load_image(dst_path)
    recon = recon[rgb, ...].transpose(1, 2, 0)
    recon = recon / recon.max()
    axs[1].imshow(recon)
    axs[1].set_axis_off()

    fig.tight_layout()
    dst_path.unlink()  # clean up


# _______________________________IMAGE PREDICTION_______________________________


def predict_image_cnn(
    src_path,
    dst_path,
    model: CNNClassifier,
    batch_size,
    patch_size=15,
    accelerator='cpu'
) -> None:
    """Predict an image with a CNNClassifier
    and save it to disk in .tif format.
    """
    # Load from disk
    image = load_image(src_path)
    dataset = PatchDatasetPostPad(image, None, patch_size=patch_size)
    loader = DataLoader(dataset, batch_size=batch_size)

    # Predict
    trainer = pl.Trainer(
        accelerator=accelerator, logger=False, enable_checkpointing=False
    )
    preds, _ = zip(*trainer.predict(model, loader))
    preds = torch.cat(preds)
    preds = preds.reshape(dataset.image.shape[-2:])

    # Write to disk
    with rasterio.open(
        dst_path,
        'w',
        height=dataset.image.shape[-2],
        width=dataset.image.shape[-1],
        count=1,
        dtype=rasterio.uint8,
        driver='Gtiff',
    ) as dst:
        dst.write(preds.numpy().astype(rasterio.uint8)[np.newaxis, ...] + 1)


def predict_image_unet(
    src_path,
    dst_path,
    model: UNetClassifier,
    batch_size=8,
    crop_size=64,
    stride=8,
    accelerator='cpu',
) -> None:
    """Predict an image with a UNetClassifier, using soft voting,
    and save it to disk in .tif format.
    """
    # Load from disk
    image = load_image(src_path)
    dataset = CroppedDataset(image, None, crop_size, stride, use_padding=True)
    loader = DataLoader(dataset, batch_size=batch_size)
    height = dataset.image.shape[-2]
    width = dataset.image.shape[-1]

    num_classes = model.hparams.num_classes
    pred_image = np.full((1, num_classes, height, width), 0., dtype=np.float32)

    # Predict
    trainer = pl.Trainer(
        accelerator=accelerator, logger=False, enable_checkpointing=False
    )
    _, probs = zip(*trainer.predict(model, loader))
    probs = torch.cat(probs)
    probs = probs.numpy()

    for idx in range(len(dataset)):
        min_i, min_j, max_i, max_j = dataset.get_bounds(idx)
        pred_image[0, :, min_i:max_i, min_j:max_j] += probs[idx]

    pred_image = np.argmax(pred_image, 1)

    p = dataset.padding
    s = (
        slice(p[0][0], -p[0][1] if p[0][1] > 0 else None),
        slice(p[1][0], -p[1][1] if p[1][1] > 0 else None)
    )
    pred_image = pred_image[:, s[0], s[1]]

    # Write to disk
    with rasterio.open(
        dst_path,
        'w',
        height=height,
        width=width,
        count=1,
        dtype=rasterio.uint8,
        driver='Gtiff',
    ) as dst:
        dst.write((pred_image).astype(rasterio.uint8) + 1)


def predict_all_images(
    predict_fn,
    suffix,
    paths,
    model,
    batch_size,
    cmap,
    norm,
    class_names,
    rgb,
    output_dir,
    accelerator='cpu'
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    for src_path in paths:
        src_path = Path(src_path)
        tiff_dst_path = output_dir / Path(src_path.stem + f'_pred{suffix}.tif')
        png_dst_path = output_dir / Path(src_path.stem + f'_pred{suffix}.png')

        predict_fn(
            src_path, tiff_dst_path, model, batch_size, accelerator=accelerator
        )

        image = load_image(src_path)
        label = load_label(tiff_dst_path)
        display_image_and_label(
            image=image,
            label=label,
            cmap=cmap,
            norm=norm,
            class_names=class_names,
            rgb=rgb,
            title=src_path.stem + suffix,
        )

        plt.savefig(png_dst_path, facecolor='white', bbox_inches='tight')


def get_latest_checkpoint(output_dir) -> Path:
    output_dir = Path(output_dir)
    ckpts = list(output_dir.glob('lightning_logs/**/*.ckpt'))
    pattern = re.compile(
        r'.*?version_(\d+)/checkpoints/epoch=(\d+)-step=(\d+).ckpt$'
    )
    matches = (pattern.findall(path.as_posix()) for path in ckpts)
    zipped = ((c, tuple(map(int, m[0]))) for c, m in zip(ckpts, matches) if m)
    latest_ckpt, _ = max(zipped, key=itemgetter(1))
    return latest_ckpt
