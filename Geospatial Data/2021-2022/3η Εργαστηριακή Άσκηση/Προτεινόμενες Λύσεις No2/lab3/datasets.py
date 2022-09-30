from typing import Optional, Union, Tuple
import random

import numpy as np
import torch
from torch.utils.data import Dataset, random_split
import torchvision.transforms.functional as TF


class PatchDatasetNoPad(Dataset):
    """Patches of specified size around the pixels whose label is non zero.
    No use of padding.
    Instead, ignore pixels whose patch doesn't lie inside the image.
    """

    def __init__(
        self,
        image,
        label_image,
        patch_size,
        channels=None,
        ignore_index=-1,
    ):
        super().__init__()

        self.image = image
        self.channels = channels if channels is not None else slice(None)
        self.ignore_index = ignore_index

        # Keep only the pixels that are labelled and whose patch lies inside the image
        r = patch_size // 2
        is_inner = np.full(image.shape[-2:], False, bool)
        is_inner[r:-r, r:-r] = True
        if label_image is not None:
            self.indices = np.nonzero(
                (label_image != self.ignore_index) & is_inner
            )
            self.labels = label_image[self.indices]
        else:
            self.indices = np.nonzero(is_inner)
            self.labels = None

        self.patch_size = patch_size

    def __len__(self):
        return len(self.indices[0])

    def __getitem__(self, idx):
        i, j = self.indices[0][idx], self.indices[1][idx]
        r = self.patch_size // 2
        x = self.image[self.channels, i - r:i + r + 1, j - r:j + r + 1]

        x = torch.tensor(x, dtype=torch.float32)

        if self.labels is not None:
            y = self.labels[idx]
            y = torch.tensor(y, dtype=torch.int64)
            return x, y
        else:
            return x,


class PatchDatasetPostPad(Dataset):
    """Patches of specified size around the pixels whose label is non zero.
    Slices a patch and then pads it equally on each side.
    """

    def __init__(
        self,
        image,
        label_image,
        patch_size,
        channels=None,
        ignore_index=-1,
    ):
        super().__init__()

        self.channels = channels if channels is not None else slice(None)
        self.ignore_index = ignore_index
        self.patch_size = patch_size
        self.image = image

        if label_image is not None:
            # Keep only the pixels that are labelled
            self.indices = np.nonzero(label_image != self.ignore_index)
            self.labels = label_image[self.indices]
        else:
            self.indices = tuple(map(np.ravel, np.indices(image.shape[-2:])))
            self.labels = None

    def __len__(self):
        return len(self.indices[0])

    def __getitem__(self, idx):
        i, j = self.indices[0][idx], self.indices[1][idx]
        r = self.patch_size // 2

        i_min = max(0, i - r)
        i_max = min(i + r + 1, self.image.shape[-2])
        j_min = max(0, j - r)
        j_max = min(j + r + 1, self.image.shape[-1])
        x = self.image[self.channels, i_min:i_max, j_min:j_max]

        h, w = x.shape[-2:]
        h_pad = self.patch_size - h
        w_pad = self.patch_size - w
        padding = (
            (0, 0),
            (h_pad // 2, h_pad - h_pad // 2),
            (w_pad // 2, w_pad - w_pad // 2),
        )
        x = np.pad(x, padding)

        x = torch.tensor(x, dtype=torch.float32)

        if self.labels is not None:
            y = self.labels[idx]
            y = torch.tensor(y, dtype=torch.int64)
            return x, y
        else:
            return x,


class CroppedDataset(Dataset):
    """Sliding window over an image and its label"""

    def __init__(
        self,
        image,
        label_image,
        crop_size: Union[int, Tuple[int, int]],
        stride: Union[int, Tuple[int, int]] = 1,
        channels: Optional[Tuple[int, ...]] = None,
        use_padding: bool = False,
    ):

        super().__init__()

        self.image = image
        self.labels = label_image

        if isinstance(crop_size, int):
            self.crop_h, self.crop_w = crop_size, crop_size
        elif isinstance(crop_size, tuple):
            self.crop_h, self.crop_w = crop_size
        else:
            raise ValueError('Invalid crop_size.')
        if self.crop_h > self.img_h or self.crop_w > self.img_w:
            raise ValueError('crops_size is bigger than image size.')

        if isinstance(stride, int):
            self.stride_h, self.stride_w = stride, stride
        elif isinstance(stride, tuple):
            self.stride_h, self.stride_w = stride
        else:
            raise ValueError('Invalid stride.')

        if use_padding:
            # Pad the image equally on all sides,
            # so that the sliding window can cover the entire image
            _, _, max_i, max_j = self.get_bounds(len(self) - 1)
            missed_h, missed_w = self.img_h - max_i, self.img_w - max_j
            dh = max(0, self.stride_h - missed_h)
            dw = max(0, self.stride_w - missed_w)
            self.padding = (dh // 2, dh - dh // 2), (dw // 2, dw - dw // 2)
            self.image = np.pad(
                self.image,
                ((0, 0),) + self.padding,
                'constant',
                constant_values=0,
            )
            if self.labels is not None:
                self.labels = np.pad(
                    self.labels, self.padding, 'constant', constant_values=-1
                )
        else:
            self.padding = None

        self.channels = channels if channels is not None else slice(None)

    def __len__(self):
        return self.n_rows * self.n_cols

    def __getitem__(self, idx):
        min_i, min_j, max_i, max_j = self.get_bounds(idx)

        x = self.image[self.channels, min_i:max_i, min_j:max_j]
        x = torch.tensor(x, dtype=torch.float32)

        if self.labels is not None:
            y = self.labels[min_i:max_i, min_j:max_j]
            y = torch.tensor(y, dtype=torch.int64)
            return x, y
        else:
            return x,

    def get_bounds(self, idx):
        # Get the box coordinates of the current position of the sliding window
        r, c = divmod(idx, self.n_cols)
        min_i, min_j = r * self.stride_h, c * self.stride_w
        max_i, max_j = min_i + self.crop_h, min_j + self.crop_w
        return min_i, min_j, max_i, max_j

    @property
    def img_h(self):
        return self.image.shape[-2]

    @property
    def img_w(self):
        return self.image.shape[-1]

    @property
    def n_rows(self):
        return 1 + (self.img_h - self.crop_h) // self.stride_h

    @property
    def n_cols(self):
        return 1 + (self.img_w - self.crop_w) // self.stride_w


class AugmentedDataset(Dataset):
    """"Wraps a dataset to include a transform"""

    def __init__(self, dataset, transform, apply_on_target=False):
        self.dataset = dataset
        self.transform = transform
        self.apply_on_target = apply_on_target

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        x, *y = self.dataset[idx]  # using * in case there's no target
        if self.apply_on_target:
            x, *y = self.transform(x, *y)
        else:
            x = self.transform(x)
        return (x, *y)


def flip_and_rotate(*tensors):
    # Use this transform only when height == width!

    tensors = list(tensors)
    # Expand 2 dimensional tensors so that the transforms work
    expanded = []
    for i in range(len(tensors)):
        if tensors[i].ndim == 2:
            tensors[i] = torch.unsqueeze(tensors[i], 0)
            expanded.append(i)

    # Flip vertically
    if random.random() > 0.5:
        tensors = [TF.vflip(t) for t in tensors]
    # Rotate by 0, 1, 2, or 3 right angles
    k = random.randint(0, 4)
    if k != 0:
        tensors = [TF.rotate(t, k * 90) for t in tensors]

    # Undo the expansion
    for idx in expanded:
        tensors[idx] = torch.squeeze(tensors[idx], 0)

    return tuple(tensors) if len(tensors) > 1 else tensors[0]


def make_pixel_dataset(images, label_images, ignore_index=-1):
    """Select pixels with non-unknown labels from a list of images.
    Return the pixel values and their labels.
    """
    x_lst = []
    y_lst = []
    for x, y in zip(images, label_images):
        mask = y != ignore_index
        y = y[mask]
        x = x[:, mask]
        x_lst.append(x)
        y_lst.append(y)
    x = np.concatenate(x_lst, 1).T
    y = np.concatenate(y_lst, 0)
    return x, y


def split_dataset(dataset, train_size, test_size=0., seed=None):
    """Splits a PyTorch Dataset into train, validation and test Subsets."""
    if not 0 <= train_size + test_size <= 1:
        raise ValueError('Invalid train/test sizes')
    n = len(dataset)
    n_train = int(train_size * n)
    n_test = int(test_size * n)
    n_val = n - (n_train + n_test)
    generator = torch.Generator()
    if seed is not None:
        generator.manual_seed(seed)
    dataset_train, dataset_val, dataset_test = random_split(
        dataset, [n_train, n_val, n_test], generator
    )
    return dataset_train, dataset_val, dataset_test
