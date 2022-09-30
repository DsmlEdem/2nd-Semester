# Oriented Object Detection with MMRotate

![port-image](../logo.png)

## Project's Presentation

[**presentation.pdf**](presentation.pdf)

## Installation

MMRotate is based on MMDetection, which in turn is based on MMCV. MMCV is the base of all [OpenMMLab projects](https://github.com/open-mmlab/).

To install MMRotate, a careful selection of package versions is required. See
[MMRotate installation](https://mmrotate.readthedocs.io/en/latest/install.html#installation),
[MMRotate FAQ](https://mmrotate.readthedocs.io/en/latest/faq.html),
[MMDetection installation](https://mmdetection.readthedocs.io/en/latest/get_started.html#installation),
[MMDetection FAQ](https://mmdetection.readthedocs.io/en/latest/faq.html),
[MMCV installation](https://mmcv.readthedocs.io/en/latest/get_started/installation.html),
and [Pytorch Installation](https://pytorch.org/get-started/previous-versions/). An [MMRotate Dockerfile](./docker/mmr/Dockerfile) and an [MMDetection Dockerfile](./docker/mmd/Dockerfile) are included to setup working environments (the official dockerfiles don't work).

To install with pip, the following works for GPUs that support CUDA 11.3.

```shell
pip install -U torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 \
    --extra-index-url https://download.pytorch.org/whl/cu113
pip install mmcv-full==1.6.0 -f https://download.openmmlab.com/mmcv/dist/cu113/torch1.11.0/index.html
pip install mmdet==2.25.1 mmengine==0.1.0 shapely==1.8.4 tensorboard==2.10.0 jupyter==1.0.0
git clone https://github.com/open-mmlab/mmrotate.git
cd mmrotate
git checkout tags/v0.3.2
pip install -v -e .

```

After installation, there should be an `mmrotate` directory (git repo clone) inside the working directory. The most common usage is to `cd` inside this directory and do all the work inside it.

## Existing Documentation

To learn how to use [MMRotate](https://mmrotate.readthedocs.io/en/latest/), it is recommended to start with [MMCV](https://mmcv.readthedocs.io/en/latest/) first. There are also good tutorials in the [MMRotate demo directory](https://github.com/open-mmlab/mmrotate/tree/main/demo). Sadly, the documentation is lacking and looking up for answers on the internet usually won't return any relevant results. For this reason, it is often the case that one needs to browse the source code to understand the project's usage, even for basic things.

## Setting up a DOTA-formatted dataset

[Download DOTA v1.0](https://captain-whu.github.io/DOTA/) or transform the labels of a different dataset into the [DOTA format](https://mmrotate.readthedocs.io/en/latest/tutorials/customize_dataset.html).

Create a `data` directory inside `mmrotate` containing the following directory structure

```none
DOTA
├── test
│   └── images
├── train
│   ├── images
│   └── labelTxt
└── val
    ├── images
    └── labelTxt
```

Produce a new dataset by cropping the original images into `1024 x 1024` patches with an overlap of `200` by running

```shell
python tools/data/dota/split/img_split.py \
  --base-json tools/data/dota/split/split_configs/ss_train.json

python tools/data/dota/split/img_split.py \
  --base-json tools/data/dota/split/split_configs/ss_val.json

python tools/data/dota/split/img_split.py \
  --base-json tools/data/dota/split/split_configs/ss_test.json
```

The following structure will be created under `mmrotate/data`

```none
split_ss_dota/
├── test
│   ├── {datetime}.log
│   ├── annfiles
│   └── images
├── train
│   ├── {datetime}.log
│   ├── annfiles
│   └── images
└── val
    ├── {datetime}.log
    ├── annfiles
    └── images
```

## Creating a Configuration

For a configuration to work with the dataset, one can inherit from the [configs/\_base\_/dotav1.py](https://github.com/open-mmlab/mmrotate/blob/main/configs/_base_/datasets/dotav1.py) configuration and then set the appropriate paths. A simple configuration file for training can look like this

```python
# myconfig.py

_base_ = './configs/oriented_rcnn/oriented_rcnn_r50_fpn_1x_dota_le90.py'

# classes = ['foo', 'bar']  # Use this for a different DOTA-formatted dataset.
data_root = './data/split_ss_dota/'
data = dict(
    samples_per_gpu=3,
    workers_per_gpu=2,
    train=dict(
        img_prefix='./data/split_ss_dota/train/images/',
        ann_file='./data/split_ss_dota/train/annfiles/'),
    val=dict(
        img_prefix='./data/split_ss_dota/val/images/',
        ann_file='./data/split_ss_dota/val/annfiles/'),
    test=dict(
        img_prefix='./data/split_ss_dota/test/images/',
        ann_file='./data/split_ss_dota/test/images/'))

log_config = dict(
    hooks=[dict(type='TextLoggerHook'), dict(type='TensorboardLoggerHook')])

runner = dict(
    max_epochs=13)
seed = 42
gpu_ids = range(1)
device = 'cuda'

evaluation = dict(
    save_best='mAP')
```

Notice that the annotations' directory for the test set is configured to be the images' directory. See [`DOTADataset`'s source code](https://github.com/open-mmlab/mmrotate/blob/c62f148fcc2c8253218e67f2277cb8770bcd7df0/mmrotate/datasets/dota.py#L57).

You can see the full configuration with all the details from the `_base_` configurations, by running 

```shell
python tools/misc/print_config.py myconfig.py
```

## Training and Evaluating

To train with `myconfig.py`, run the following command

```shell
python tools/train.py myconfig.py
```

This will create checkpoints and logs inside `workdirs/myconfig/`.

To test using the best checkpoint from training, run

```shell
python tools/test.py \
    work_dirs/myconfig/myconfig.py \
    `ls work_dirs/myconfig/best_mAP_epoch_*.pth` \
    --format-only \
    --eval-options submission_dir=work_dirs/simple_config_preds/ nproc=1
```

which will create predictions for the original images (by assembling predictions on the image patches and then performing non-max suppression) inside `work_dirs/simple_config_preds/` in the format used for the [DOTA-v1.0 Evaluation Server](https://captain-whu.github.io/DOTA/evaluation.html).

You can also use the custom made [predictor.py](./predictor.py) to do inference on the original images and show/save their annotated versions. The inference is performed by cropping  the original image into `1024 x 1024` patches with step `824` (i.e. overlap `200`), as well `crop=1024//2 x 1024//2, step=824//2`, and `crop=1024*2 x 1024*2, step=824*2`(patches are resized with bilinear interpolation before they are fed to the model), and then merging the results using non-max suppression with `iou_threshold = 0.1`.

```shell
python predictor.py \
    --config work_dirs/myconfig/myconfig.py \
    --checkpoint `ls work_dirs/myconfig/best_mAP_epoch_*.pth` \
    --imagedir data/DOTA/test/images/ \
    --outdir predictions/myconfig
```

To create a confusion matrix for the validation or training set, you can run the provided modified [confusion_matrix.py](confusion_matrix.py) (fixed in the [original version](https://github.com/open-mmlab/mmrotate/blob/main/tools/analysis_tools/confusion_matrix.py) an invalid argument in `nms_rotated`, a nonfunctional `--color-theme` option, and added plotting functionality with `seaborn`).
For example

```shell
python tools/test.py \
    work_dirs/myconfig/myconfig.py \
    `ls work_dirs/myconfig/best_mAP_epoch_*.pth` \
    --out "simple_config_results.pkl" \
    --cfg-options \
        data.test.img_prefix=./data/split_ss_dota/val/images/ \
        data.test.ann_file=./data/split_ss_dota/val/annfiles/
    

python tools/analysis_tools/confusion_matrix.py
    myconfig.py \
    `ls work_dirs/myconfig/best_mAP_epoch_*.pth` \
    --out "simple_config_results.pkl" \
    --cfg-options \
        data.test.img_prefix=./data/split_ss_dota/val/images/ \
        data.test.ann_file=./data/split_ss_dota/val/annfiles/ \
    --color-theme flare --score-thr 0.3 --tp-iou-thr 0.5 --title "Simple Config Normalized Confusion Matrix"
```
