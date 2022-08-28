from typing import Union, Any

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from torch.optim import Adam
import seaborn as sns
import rasterio
import os

sns.set_style("dark")
# Normalizing images
def normalize(band):
    return (band - band.min()) / (band.max() - band.min())

# A function to visualize the RGB images
def display_rgb(tiff_file, image_name, rgb = (23,11,7)):
    image = np.dstack((normalize(tiff_file.read(rgb[0])),
                       normalize(tiff_file.read(rgb[1])),
                       normalize(tiff_file.read(rgb[2]))))
    fig, ax = plt.subplots(figsize = (15,10))
    ax.imshow(image)
    ax.set_title("RGB Image of " + image_name, fontsize = 15)
    plt.savefig(image_name + ".png")
    #plt.show()
    plt.close()

def CustomCmap(low,top):
    r1,g1,b1 = low
    r2,g2,b2 = top
    cdict = {'red': ((0, r1, r1),
                   (1, r2, r2)),
           'green': ((0, g1, g1),
                    (1, g2, g2)),
           'blue': ((0, b1, b1),
                   (1, b2, b2))}
    cmap = LinearSegmentedColormap('custom_cmap', cdict)
    return cmap

from mpl_toolkits.axes_grid1 import make_axes_locatable
import itertools

def plot_confusion_matrix(y_true, y_pred, cmap, target_names, title = None,
            ignore_index = False):
    fig, ax1 = plt.subplots(figsize = (8,8))
    cfmatrix = confusion_matrix(y_true = y_true, y_pred = y_pred) if ignore_index else\
        confusion_matrix(y_true = y_true-1, y_pred = y_pred-1)

    for ax,cm in zip([ax1],[cfmatrix]):
        im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=.2)
        plt.colorbar(im, cax=cax) #, ticks=[-1,-0.5,0,0.5,1]
        ax.set_title(title,fontsize=14)
        tick_marks = np.arange(len(target_names))
        ax.set_xticks(tick_marks)
        ax.set_xticklabels(target_names, rotation=90)
        ax.set_yticks(tick_marks)
        ax.set_yticklabels(target_names)

        fmt = 'd'
        thresh = cm.max() / 2.

        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            ax.text(j, i, format(cm[i, j], fmt), horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

        ax.set_ylabel('True label',fontsize=14)
        ax.set_xlabel('Predicted label',fontsize=14)

    plt.savefig(title.replace(" ","")+'.png', bbox_inches='tight')
    plt.close()
    #plt.show()

# Data transformer for ML classifier & MLP
def standard_dataset(raster_features, raster_labels, norm = True):
    """
    :param raster_features: The raster of features
    :param raster_labels: The raster of ground truth labels
    :return: Return features X (num samples x num features), Return labels y, (num samples x 1)
    """
    num_bands = raster_features.count  # Total number of bands
    width = raster_features.width
    height = raster_features.height
    X = np.zeros(shape=(width * height, num_bands))  # X -> Features
    y = raster_labels.read(1).flatten()  # y -> labels
    for band in range(num_bands):
        X[:, band] = raster_features.read(band + 1).flatten()
    # dropping rows that correspond to label with value 0
    mask = (y != 0)
    X,y = X[mask,:], y[mask]
    if norm:
        X = (X - X.min(axis = 0))/(X.max(axis = 0) - X.min(axis = 0))
    return X,y

# MLP Architecture

import torch
from torch import nn
from collections import OrderedDict
from torch.utils.data import Dataset

# The dataset class for the MLP
class MLP_Dataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.from_numpy(X).type(torch.float32)
        self.y = torch.from_numpy(y).type(torch.LongTensor) - 1

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx, :], self.y[idx]

# The Architecture
class MLP_Net(nn.Module):
    def __init__(self, in_features, out_features, layers=[10]):
        super(MLP_Net, self).__init__()
        num_layers = [in_features] + layers
        self.structure = OrderedDict()

        # Main Architecture
        for i, layer in enumerate(num_layers[:-1]):
            self.structure['linear' + str(i + 1)] = nn.Linear(num_layers[i], num_layers[i + 1])
            self.structure['BatchNorm' + str(i + 1)] = nn.BatchNorm1d(num_layers[i + 1])
            self.structure['ReLU' + str(i + 1)] = nn.ReLU()
            self.structure['Dropout' + str(i + 1)] = nn.Dropout(p=0.3)

        self.structure['linear' + str(i + 2)] = nn.Linear(num_layers[i + 1], out_features)
        self.linear_relu_stack = nn.Sequential(self.structure)

    def forward(self, x):
        return self.linear_relu_stack(x)

# Training loop

def training_loop(model, train_loader, val_loader, epochs,
                  lr, loss_fn, regularization=None,
                  reg_lambda=None, mod_epochs=20, early_stopping = False,
                  patience = None, verbose = None, title = None):
    optim = Adam(model.parameters(), lr=lr)
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    train_loss_list = []
    val_loss_list = []
    num_train_batches = len(train_loader)
    num_val_batches = len(val_loader)
    counter_epochs = 0

    if early_stopping:
        ear_stopping = EarlyStopping(patience= patience, verbose=verbose)

    for epoch in range(epochs):
        counter_epochs+=1
        model.train()
        train_loss, val_loss = 0.0, 0.0
        for train_batch in train_loader:
            X, y = train_batch[0].to(device), train_batch[1].to(device)
            preds = model(X)
            loss = loss_fn(preds, y)
            train_loss += loss.item()

            # Regulirization
            if regularization == 'L2':
                l_norm = sum(p.pow(2.0).sum() for p in model.parameters())
                loss = loss + reg_lambda * l_norm
            elif regularization == 'L1':
                l_norm = sum(p.abs().sum() for p in model.parameters())
                loss = loss + reg_lambda * l_norm

            # Backpropagation
            optim.zero_grad()
            loss.backward()
            optim.step()
        model.eval()
        with torch.no_grad():
            for val_batch in val_loader:
                X, y = val_batch[0].to(device), val_batch[1].to(device)
                preds = model(X)
                val_loss += loss_fn(preds, y).item()
        train_loss /= num_train_batches
        val_loss /= num_val_batches
        train_loss_list.append(train_loss)
        val_loss_list.append(val_loss)
        if (epoch + 1) % mod_epochs == 0:
            print(
                f"Epoch: {epoch + 1}/{epochs}{5 * ' '}Training Loss: {train_loss:.4f}{5 * ' '}Validation Loss: {val_loss:.4f}")

        if early_stopping:
            ear_stopping(val_loss, model)
            if ear_stopping.early_stop:
                print("Early stopping")
                break

    fig, ax = plt.subplots(figsize=(8, 8))
    sns.set_style("dark")
    ax.plot(range(1, counter_epochs + 1), train_loss_list, label='Train Loss')
    ax.plot(range(1, counter_epochs + 1), val_loss_list, label='Val Loss')
    ax.set_title("Train - Val Loss")
    ax.set_ylabel("Loss")
    ax.set_xlabel("Epochs")
    plt.legend()
    plt.savefig(title.replace(" ","") + ".png")
    plt.close()
    #plt.show()

    if early_stopping:
        model.load_state_dict(torch.load("checkpoint.pt"))

    return model, train_loss, val_loss


def test_loop(model, test_dloader, device='cpu'):
    predictions_list = np.array([], dtype=np.int64)
    targets_list = np.array([], dtype=np.int64)
    model.eval()

    for val_sample in test_dloader:
        X = val_sample[0].to(device)
        y = val_sample[1].cpu().numpy()
        targets_list = np.concatenate((targets_list, y))

        with torch.no_grad():
            preds = model(X)
            predictions_list = np.concatenate((predictions_list,
                                               torch.argmax(preds, dim=-1).cpu().numpy()))
    return predictions_list, targets_list


# CNN - Patch based

from typing import Callable, List
import torch.nn.functional as F

def normalize_patch(factor:int=10000):
    def apply(x: np.array) -> np.array:
        x = x.astype(np.float32) / factor
        return x
    return apply

TransformFun = Callable[[np.array], np.array]

class patching_dataset(Dataset):
    def __init__(self, path, img_name, patch_size, center_stride,
                 normalization:List[TransformFun] = [],
                 channels = None):
        """
        :param path: The path of the tiff files
        :param img_name: The name of the image, e.g. Dioni
        :param patch_size: The patch size, e.g. 15
        :param center_stride: The vertical & horizontal stride of centers
        :param normalization: normalization to be applied
        :param channels: Which channels to keep
        """
        self.patch_size = patch_size
        self.center_stride = center_stride
        self.step = (self.patch_size-1)//2
        self.raster = rasterio.open(os.path.join(path,img_name + ".tif"))
        self.height = self.raster.height
        self.width = self.raster.width
        self.labels = np.squeeze(rasterio.open(os.path.join(path,img_name + "_GT.tif")).read())
        self.features = self.raster.read() # Shape: C x H x W
        self.centers = []
        self.center_labels = []
        self.normalization = normalization
        self.channels = channels if channels is not None else slice(None)

        self.find_centers()

    def find_centers(self):
        """
        Find all centers with vertical/horizontal distance
        at least equal to center stride
        """
        max_width = self.width - 1 - self.step
        min_width = self.step
        max_height = self.height -1 - self.step
        min_height = self.step

        for i in range(self.step, self.height - self.step, self.center_stride): # Loop over height
            prev_row_pos = 0
            for j in range(self.step, self.width - self.step): # Loop over width
                condition = (min_width <= j <= max_width) and (min_height <= i <= max_height) and \
                            (j-prev_row_pos >= self.center_stride) and (self.labels[i,j] != 0)
                if condition:
                    self.centers.append((i, j))
                    self.center_labels.append(self.labels[i, j])
                    prev_row_pos = j
        self.center_labels = np.array(self.center_labels)

    def __getitem__(self, idx):
        i,j = self.centers[idx]  # i: height, j: width
        X = self.features[self.channels, i-self.step: i+self.step+1, j-self.step: j+self.step+1]
        y = self.center_labels[idx]
        for T in self.normalization:
            X = T(X)
        return torch.tensor(X, dtype = torch.float32), torch.tensor(y-1, dtype = torch.int64)

    def __len__(self):
        return len(self.centers)


# A simple CNN

class CNN(nn.Module):
    def __init__(self, channels_in, num_classes):
        super(CNN, self).__init__()

        self.stem = nn.Sequential(
            nn.Conv2d(channels_in, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

        self.block1 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

        self.block2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

        self.block3 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

        self.classifier = nn.Sequential(
            nn.Linear(4 * 4 * 64, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.stem(x)
        x = x + self.block1(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = x + self.block2(x)
        x = F.max_pool2d(x, kernel_size=2, stride=2)
        x = x + self.block3(x)
        x = F.adaptive_avg_pool2d(x, output_size=(4, 4))

        return self.classifier(x.view(-1, 4 * 4 * 64))

class augmented_dataset(Dataset):
    def __init__(self, dataset, transforms, apply_on_target = False):
        self.dataset = dataset
        self.transforms = transforms
        self.apply_on_target = apply_on_target

    def __getitem__(self, idx):
        X,y = self.dataset[idx]
        X = X.numpy()
        y = y.numpy()
        if self.transforms is not None:
            if self.apply_on_target == False:
                augmentations = self.transforms
                X = augmentations(image = np.transpose(X,(1,2,0)))["image"]
                X = np.transpose(X,(2,0,1))
            else:
                transformed = self.transforms(image = np.transpose(X, (1,2,0)),
                                              mask = y)
                X = torch.tensor(np.transpose(transformed["image"], (2,0,1)), dtype=torch.float32)
                y = torch.tensor(transformed["mask"], dtype=torch.int64)

        return X,y
    def __len__(self):
        return len(self.dataset)

from torchvision.models.resnet import resnet18

class TransferResNet(nn.Module):
    def __init__(self, n_classes, freeze_head):
        super(TransferResNet,self).__init__()

        self.model = resnet18(pretrained=True, progress=False)
        self.freeze_head = freeze_head
        if self.freeze_head:
            for param in self.model.parameters():
                param.requires_grad = False
        self.fts_in = self.model.fc.in_features
        self.model.fc = nn.Linear(self.fts_in, 256)

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, n_classes)
        )

    def forward(self,x):
        x = self.model(x)
        return self.classifier(x)

from torch.utils.data import random_split
from torch.utils.data import ConcatDataset

def prepare_datasets(training_path, train_test_ratio, train_val_ratio,
                     type, combined = True, channels = None, patch_size = None,
                     center_stride = None, crop_size = None):
    if type == "Patches":
        dioni_dataset = patching_dataset(path = training_path, img_name="Dioni",
                                     patch_size=patch_size, center_stride=center_stride,
                                         channels=channels, normalization=[normalize_patch()])
        loukia_dataset = patching_dataset(path=training_path, img_name="Loukia",
                                          patch_size=patch_size, center_stride=center_stride,
                                          channels=channels, normalization=[normalize_patch()])
    elif type == "Cropped":
        dioni_dataset = cropped_dataset(path = training_path, img_name="Dioni",
                                        crop_size=crop_size, channels=channels,
                                        normalization=[normalize_patch()])
        loukia_dataset = cropped_dataset(path = training_path, img_name="Loukia",
                                         crop_size=crop_size, channels=channels,
                                         normalization=[normalize_patch()])
    if combined:
        train_set = ConcatDataset([dioni_dataset, loukia_dataset])
        p1 = int(train_test_ratio*len(train_set))
        train_set, test_set = random_split(train_set,[p1,len(train_set)-p1])
        p2 = int(train_val_ratio*len(train_set))
        train_set, val_set = random_split(train_set,[p2,len(train_set)-p2])
    else:
        p1 = int(train_val_ratio*len(dioni_dataset))
        train_set, val_set = random_split(dioni_dataset,[p1,len(dioni_dataset)-p1])
        test_set = loukia_dataset
    return train_set, val_set, test_set


class cropped_dataset(Dataset):
    def __init__(self, path, img_name, crop_size, normalization:List[TransformFun] = [],
                 channels = None):
        self.crop_size = crop_size
        self.path = path
        self.img_name = img_name
        self.channels = channels if channels is not None else slice(None)
        self.normalization = normalization

        # Reading the image
        self.image = rasterio.open(os.path.join(path,img_name + ".tif"))
        self.width = self.image.width
        self.height = self.image.height
        self.image = self.image.read()
        self.labels = np.squeeze(rasterio.open(os.path.join(path, img_name + "_GT.tif")).read())

        # Bounds of up-right corner of the cropped image
        self.max_width = self.width - 1 - self.crop_size
        self.max_height = self.height - 1 - self.crop_size

        self.up_left_corners = [] # the up-left corners of the cropped images

        self.find_up_left_corners()

    def find_up_left_corners(self):
        for row in range(0, self.max_height, self.crop_size):
            for col in range(0, self.max_width, self.crop_size):
                self.up_left_corners.append((row,col))

    def __getitem__(self, idx):
        i,j = self.up_left_corners[idx]
        X = self.image[self.channels, i:i+self.crop_size, j:j+self.crop_size]
        y = self.labels[i:i+self.crop_size, j:j+self.crop_size]
        for T in self.normalization:
            X = T(X)
        return torch.tensor(X, dtype = torch.float32), torch.tensor(y-1, dtype=torch.int64)

    def __len__(self):
        return len(self.up_left_corners)


# Unet Architecture
import torchvision.transforms.functional as TF

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, stride = 1, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self,x):
        return self.conv(x)


class UNet(nn.Module):
    def __init__(self, in_channels, out_channels, features = [64, 128, 256, 512]):
        super(UNet, self).__init__()
        self.down_part = nn.ModuleList()
        self.up_part = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Encoder Part
        for feature in features:
            self.down_part.append(DoubleConv(in_channels, feature))
            in_channels = feature
        # Decoder Part
        for feature in reversed(features):
            self.up_part.append(
                nn.ConvTranspose2d(feature*2, feature, kernel_size=2, stride=2)
            )
            self.up_part.append(DoubleConv(2*feature, feature))
        self.bottleneck = DoubleConv(features[-1], features[-1]*2)
        self.output = nn.Conv2d(features[0], out_channels, kernel_size=1, stride=1)

    def forward(self, x):
        skip_connections = []
        for down in self.down_part:
            x = down(x)
            skip_connections.append(x)
            x = self.pool(x)
        x = self.bottleneck(x)
        skip_connections = skip_connections[::-1]
        for idx in range(0, len(self.up_part), 2):
            x = self.up_part[idx](x)
            skip_connection = skip_connections[idx//2]

            if x.shape != skip_connection.shape:
                x = TF.resize(x, size = skip_connection.shape[2:])

            concat_skip = torch.cat((skip_connection,x), dim = 1)
            x = self.up_part[idx + 1](concat_skip)

        return self.output(x)


def segmentation_test_loop(model, test_loader, ignore_index = -1, device = "cpu"):
    predictions_list = np.array([], dtype=np.int64)
    targets_list = np.array([], dtype=np.int64)
    model.eval()

    for val_sample in test_loader:
        X = val_sample[0].to(device)
        y = val_sample[1].cpu().numpy().flatten()
        mask = (y != ignore_index)
        y = y[mask]
        targets_list = np.concatenate((targets_list, y))

        with torch.no_grad():
            preds = torch.argmax(model(X), dim=1).cpu().numpy().flatten()
            preds = preds[mask]
            predictions_list = np.concatenate((predictions_list, preds))
    return predictions_list, targets_list


# Source: https://github.com/Bjarten/early-stopping-pytorch/blob/master/pytorchtools.py

class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""
    def __init__(self, patience=7, verbose=False, delta=0, path='checkpoint.pt', trace_func=print):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation loss improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
            trace_func (function): trace print function.
                            Default: print
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = path
        self.trace_func = trace_func
    def __call__(self, val_loss, model):

        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            self.trace_func(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        '''Saves model when validation loss decrease.'''
        if self.verbose:
            self.trace_func(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss

from torch.utils.data import DataLoader

def predict_image(path, img_name, model, which_model, cropp_size, device):
    raster = rasterio.open(os.path.join(path, img_name+".tif"))
    height = raster.height
    width = raster.width
    val_img = np.zeros(shape = (height, width))
    if which_model == "center":
        data = validation_dataset(raster = raster, which_model=which_model,
                                  img_size=cropp_size, normalization=[normalize_patch()])
        data_loader = DataLoader(dataset=data)
        for idx, x in enumerate(data_loader):
            row, col = divmod(idx, width)
            pred = (torch.argmax(model(x.to(device)),dim=1).cpu().numpy()+1).squeeze()
            val_img[row,col] = pred
    elif which_model == "corner":
        data = validation_dataset(raster = raster, which_model=which_model,
                                  img_size=cropp_size, normalization=[normalize_patch()])
        data_loader = DataLoader(dataset=data)

        for idx, x in enumerate(data_loader):
            row, col = data.corners[idx]
            row_end, col_end = min(row+cropp_size,height), min(col+cropp_size,width)
            pred = (torch.argmax(model(x.to(device)), dim=1).cpu().numpy() + 1).squeeze()
            pred = pred[:row_end - row,:col_end - col]
            val_img[row:row_end,col:col_end] = pred
    else:
        raise ValueError("Incorrect model type. Either 'center' or 'corner'.")
    return val_img

class validation_dataset(Dataset):
    def __init__(self, raster, which_model, img_size, normalization:List[TransformFun] = [],
                 channels = 176):
        self.raster = raster
        self.features = raster.read()
        self.channels = channels
        self.which_model = which_model
        self.img_size = img_size
        self.height = self.raster.height
        self.width = self.raster.width
        self.normalization = normalization
        self.corners = []
        if self.which_model == "corner":
            self.find_corners()

    def __getitem__(self, idx):
        if self.which_model == "center":
            row, col = divmod(idx, self.width)
            d = self.img_size // 2
            r1_min,r1_max, c1_min,c1_max = row-d,row+d,col-d,col+d
            r2_min,r2_max, c2_min,c2_max = max(0,r1_min), min(self.height-1,r1_max), max(0,c1_min), min(self.width-1,c1_max)
            x_hat = self.features[:,r2_min:r2_max+1, c2_min:c2_max+1]
            top,left,right,down = d-(row-r2_min), d - (col-c2_min), d-(r2_max-row), d-(c2_max-col)
            x_hat = np.pad(x_hat, [(0,0), (top,down), (left,right)], mode="constant")
            for T in self.normalization:
                x_hat = T(x_hat)
            return torch.tensor(x_hat, dtype=torch.float32)

        elif self.which_model == "corner":
            row,col = self.corners[idx]
            r1_max, c1_max = row + self.img_size - 1, col + self.img_size - 1
            r2_max, c2_max = min(self.height-1, r1_max), min(self.width-1,c1_max)
            x_hat = self.features[:, row:r2_max+1, col:c2_max+1]
            down,right = self.img_size-(r2_max-row+1), self.img_size - (c2_max-col+1)
            x_hat = np.pad(x_hat, [(0,0), (0,down), (0,right)], mode = "constant")
            for T in self.normalization:
                x_hat = T(x_hat)
            return torch.tensor(x_hat, dtype=torch.float32)
        else:
            raise ValueError("Input should be either 'center' or 'corner'.")

    def __len__(self):
        if self.which_model == "center":
            return self.height*self.width
        else:
            return len(self.corners)

    def find_corners(self):
        for row in range(0, self.height, self.img_size):
            for col in range(0, self.width, self.img_size):
                self.corners.append((row,col))

import matplotlib.colors
def plot_labeled_image(img,target_names, title, zero_included = None):
    colors = ["#e6004d", "#a600cc", "#ffffa8", "#f2a64d", "#e6a600",
              "#80ff00", "#00a600", "#a600cc", "#819c25", "#e6cc4d",
              "#e6e64d", "#cccccc", "#4d4dff", "#80f2e6"]
    if zero_included is not None:
        colors.insert(0,"#000000")
        target_names.insert(0, "Non defined")
    else:
        img -= 1
    colormap = matplotlib.colors.ListedColormap(colors)

    plt.figure(figsize=(15,10))
    im = plt.imshow(img, cmap=colormap,interpolation=None,
                    vmin = -0.5, vmax=len(target_names)-0.5)
    cbar = plt.colorbar(im, ticks = range(len(target_names)))
    cbar.ax.set_yticklabels(target_names)
    plt.title(title)
    plt.savefig(title.replace(" ","")+".png")
    plt.close()

import matplotlib as mpl
def plot_img_labels(tiff, labels, target_names, title1, title2, save_title,
                    zero_included = None, rgb = (23,11,7)):
    colors = ["#e6004d", "#a600cc", "#ffffa8", "#f2a64d", "#e6a600",
              "#80ff00", "#00a600", "#a600cc", "#819c25", "#e6cc4d",
              "#e6e64d", "#cccccc", "#4d4dff", "#80f2e6"]
    if zero_included is not None:
        colors.insert(0,"#000000")
        target_names.insert(0, "Non defined")
    else:
        labels -= 1
    colormap = matplotlib.colors.ListedColormap(colors)

    image = np.dstack((normalize(tiff.read(rgb[0])),
                       normalize(tiff.read(rgb[1])),
                       normalize(tiff.read(rgb[2]))))
    fig, ax = plt.subplots(figsize = (16,6), nrows=2)
    ax[0].imshow(image)
    ax[1].imshow(labels, cmap=colormap)
    ax[0].set_axis_off()
    ax[1].set_axis_off()
    ax[0].set_title(title1)
    ax[1].set_title(title2)
    norm = mpl.colors.Normalize(0, colormap.N)
    cbar = plt.gcf().colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=colormap),
        ax=ax, shrink=0.9, location='right'
    )
    cbar.set_ticks(0.5 + np.arange(colormap.N))
    cbar.set_ticklabels(target_names)
    plt.savefig(save_title+".png")
    plt.close()

def write_tif(path,img):
    with rasterio.open(
        path, 'w',
        width = img.shape[1],
        height = img.shape[0],
        count=1,
        dtype = rasterio.uint8,
        driver ='Gtiff'
    ) as dst:
        dst.write(img.astype(rasterio.uint8),1)
