# %%
import itertools
from pathlib import Path
from typing import (
    Callable, Dict, List, Optional, Tuple
)

import numpy as np
import torch
from torch import Tensor
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader
from torchvision.models import ResNet50_Weights
from torchvision.utils import draw_bounding_boxes
import torchvision.transforms.functional as TF
from torchvision.io import read_image, ImageReadMode
from torch.utils.tensorboard import SummaryWriter  # type: ignore

from torchvision.models.detection.backbone_utils import BackboneWithFPN
from torchvision.models.detection.roi_heads import RoIHeads
from torchvision.models.detection.rpn import RegionProposalNetwork
from torchvision.models.detection.transform import (
    GeneralizedRCNNTransform, ImageList
)
from torchvision.models.detection.faster_rcnn import (
    fasterrcnn_resnet50_fpn_v2, FasterRCNN
)
from torchvision.models.detection.retinanet import retinanet_resnet50_fpn_v2

import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
import albumentations as A
from tqdm import tqdm

# IMPORTANT: Install torchmetrics via
# pip install git+https://github.com/k-papadakis/metrics.git#egg=torchmetrics
# otherwise MeanAveragePrecision might not work.
# See this https://github.com/Lightning-AI/metrics/issues/1147
from torchmetrics.detection.mean_ap import MeanAveragePrecision


class ObjectsDataset(Dataset):
    
    class_names = ['battery', 'dice', 'toycar', 'candle', 'highlighter', 'spoon']

    def __init__(
        self,
        root_dir,
        mode,
        transform: Optional[Callable[[Tensor, Tensor], Tuple[Tensor, Tensor]]] = None
    ) -> None:
        """"Object Detection: Batteries, Dice, and Toy Cars" from Kaggle.
        See https://www.kaggle.com/datasets/markcsizmadia/object-detection-batteries-dices-and-toy-cars?select=dataset
        """
        super().__init__()
        self.root_dir = Path(root_dir)
        self.mode = mode
        self.image_names = sorted(
            p.stem for p in (self.root_dir / self.mode / 'images').iterdir()
        )
        self.class_name_to_int = {
            name: i for i, name in enumerate(self.class_names, 1)
        }
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_names)

    def __getitem__(self, idx: int):
        name = self.image_names[idx]
        image_path = self.root_dir / self.mode / 'images' / f'{name}.jpg'
        targets_path = self.root_dir / self.mode / 'labels' / f'{name}.txt'

        image = read_image(str(image_path), ImageReadMode.RGB)
        image = TF.convert_image_dtype(image, torch.float32)

        targets_tensor = torch.from_numpy(
            np.loadtxt(
                targets_path,
                usecols=(0, *range(4, 8)),
                dtype=np.int64,
                encoding=None,
                converters={0: self.class_name_to_int.get},
                ndmin=2,
            )
        )
        labels, boxes = targets_tensor[:, 0], targets_tensor[:, 1:]
        
        if self.transform is not None:
            image, boxes = self.transform(image, boxes)

        targets = {
            'labels': labels,
            'boxes': boxes,
        }
        return name, image, targets


class TorchAlbumentations:
    
    def __init__(self, transform):
        """Wrapper around an Albumentations transform to handle type and name conversions."""
        self.transform = transform
    
    def __call__(self, image: Tensor, boxes: Tensor) -> Tuple[Tensor, Tensor]:
        image = torch.permute(image, (1, 2, 0))
        transformed = self.transform(
            image=image.cpu().numpy(),
            bboxes=boxes.cpu().numpy()
        )
        t_image = torch.from_numpy(transformed['image'])
        t_image = torch.permute(t_image, (2, 0, 1))
        t_boxes = torch.tensor(transformed['bboxes']).to(torch.int64)
        return t_image, t_boxes


def get_transform() -> TorchAlbumentations:
    transform = TorchAlbumentations(A.Compose(
        [
            A.HorizontalFlip(),
            A.RandomRotate90(),
            A.RandomBrightnessContrast(),
        ],
        bbox_params=A.BboxParams(format='pascal_voc', label_fields=[])
    ))
    return transform


def get_fasterrcnn(num_classes: Optional[int] = None) -> FasterRCNN:
    fasterrcnn = fasterrcnn_resnet50_fpn_v2(
        weights_backbone=ResNet50_Weights.DEFAULT,
        num_classes=num_classes
    )
    return fasterrcnn


def transpose(batch):
    return tuple(map(list, zip(*batch)))


def create_dataloaders(
    dataset_train: Dataset,
    dataset_val: Dataset,
    dataset_test: Dataset,
    batch_size: int,
    collate_fn: Optional[Callable] = None,
    num_workers: int = 0,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    loader_train = DataLoader(
        dataset_train,
        shuffle=True,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    loader_val = DataLoader(
        dataset_val,
        shuffle=False,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    loader_test = DataLoader(
        dataset_test,
        shuffle=False,
        collate_fn=collate_fn,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    return loader_train, loader_val, loader_test


class LitDetector(pl.LightningModule):
    
    def __init__(
        self,
        num_classes: int,
        lr: float = 1e-4,
        class_names: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """Basic functionality for an object detection model.
        Mean average precision and related metrics are logged on each validation and test epoch ending.
        During testing, all the images with predicted boxes and classes are logged.
        
        `num_classes` includes the background
        `label_names` does not include the background
        
        To log any other hyperparameters, pass them as keyword arguments.
        """
        super().__init__()
        self.save_hyperparameters()
        self.lr = lr
        if class_names is None:
            self.class_names = list(map(str, range(1, num_classes)))
        else:
            self.class_names = class_names
        self.val_mean_ap = MeanAveragePrecision()
        self.test_mean_ap = MeanAveragePrecision(class_metrics=True)
        self.epoch_counter = 0
    
    def shared_val_test_step(
        self, batch
    ):
        raise NotImplementedError
    
    def validation_step(
        self,
        batch,
        batch_idx: int,
    ) -> None:
        _, _, targets, detections = self.shared_val_test_step(batch)
        self.val_mean_ap.update(detections, targets)  # type: ignore

    def test_step(
        self,
        batch,
        batch_idx: int
    ) -> None:
        image_names, images, targets, detections = self.shared_val_test_step(batch)
        self.test_mean_ap.update(detections, targets)  # type: ignore
        self.log_images(images, detections, image_names)

    def log_images(
        self,
        images: List[Tensor],
        detections,
        image_names: List[str],
    ) -> None:    
        """Log images with boxes and labels to TensorBoard"""
        tensorboard: SummaryWriter = self.logger.experiment  # type: ignore
        for name, img, dt in zip(image_names, images, detections):
            labels = [
                f'{self.class_names[k - 1]}:{s:.0%}'
                for k, s in zip(dt['labels'], dt['scores'])
            ]
            img = draw_bounding_boxes(
                image=TF.convert_image_dtype(img, torch.uint8),
                labels=labels,
                boxes=dt['boxes'],
            )
            tensorboard.add_image(tag=name, img_tensor=img)
        
    def validation_epoch_end(self, outputs) -> None:
        metrics = self.val_mean_ap.compute()
        self.log_dict({f'val_{k}': v for k, v in metrics.items()})
        self.val_mean_ap.reset()

    def test_epoch_end(self, outputs) -> None:
        metrics = self.test_mean_ap.compute()

        map_per_class = metrics.pop('map_per_class')
        mar_100_per_class = metrics.pop('mar_100_per_class')

        metrics.update(
            (f'map_class_{label}', x) 
            for label, x in zip(self.class_names, map_per_class)
        )
        metrics.update(
            (f'mar_100_class_{label}', x)
            for label, x in zip(self.class_names, mar_100_per_class)
        )

        self.log_dict({f'test_{k}': v for k, v in metrics.items()})
        self.test_mean_ap.reset()
        
    def on_train_epoch_start(self) -> None:
        print(f'Epoch {self.epoch_counter}')
        self.epoch_counter += 1


class LitRetinaNet(LitDetector):
    
    def __init__(self, num_classes: int, lr: float = 0.0001, class_names: Optional[List[str]] = None, **kwargs) -> None:
        super().__init__(num_classes, lr, class_names, **kwargs)
        self.model = retinanet_resnet50_fpn_v2(
            weights_backbone=ResNet50_Weights.DEFAULT,
            num_classes=num_classes
        )
    
    def forward(
        self,
        images: List[Tensor],
        targets = None,
    ):
        return self.model(images, targets)
    
    def configure_optimizers(self):
        return Adam(self.model.parameters(), self.lr)
    
    def training_step(self, batch, batch_idx: int) -> Tensor:
        _, images, targets = batch
        losses = self(images, targets)
        loss = losses['bbox_regression'] + losses['classification']
        self.log_dict({
            **{f'train_{k}': v for k, v in losses.items()},  # type: ignore
            **{'train_loss': loss}
        })
        return loss

    def shared_val_test_step(
        self, batch
    ):
        image_names, images, targets = batch
        detections = self(images)    
        return image_names, images, targets, detections


def train_retinanet(
    data_dir,
    output_dir,
    batch_size: int,
    accelerator: str,
    num_workers: int,
) -> str:
    print('Training RetinaNet')
    dataset_train = ObjectsDataset(data_dir, mode='train', transform=get_transform())
    dataset_val = ObjectsDataset(data_dir, mode='val')
    dataset_test = ObjectsDataset(data_dir, mode='test')
    loader_train, loader_val, loader_test = create_dataloaders(
        dataset_train,
        dataset_val,
        dataset_test,
        batch_size=batch_size,
        collate_fn=transpose,
        num_workers=num_workers,
    )
    retinanet_dir = Path(output_dir, 'retinanet')
    class_names = ObjectsDataset.class_names
    num_classes = 1 + len(class_names)  # Including background
    
    model = LitRetinaNet(num_classes=num_classes, lr=1e-4, class_names=class_names)
    trainer = pl.Trainer(
        default_root_dir=str(retinanet_dir),
        callbacks=[
            EarlyStopping(monitor='val_map', mode='max', patience=30, verbose=True),
            ModelCheckpoint(monitor='val_map', mode='max'),
        ],
        max_epochs=110,
        accelerator=accelerator,
        log_every_n_steps=10,
        val_check_interval=0.5
    )
    trainer.fit(model, loader_train, loader_val)
    trainer.test(ckpt_path='best', dataloaders=loader_test)
    
    ckpt: str = trainer.checkpoint_callback.best_model_path  # type: ignore
    return ckpt


class LitFasterRCNN(LitDetector):

    def __init__(
        self,
        num_classes: int,
        lr: float = 1e-4,
        phase = 1,
        class_names: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        
        """Faster R-CNN 4-Step Alternating Training.
        
        Model structure
            - Phases 1 and 3: The model consists of only the Backbone (Resnet50) and the RPN.
            - Phase 2: The model consists of only the Backbone and the ROI Heads,
              and the proposals are part of the input (cached proposals from phase 1).
            - Phase 4: The model is a complete Faster R-CNN.
            
        Model forward
            - Phases 1 and 3: Returns the proposal losses if training, else returns the proposals.
              The combined loss is the sum of the proposal losses.
            - Phases 2 and 4: Returns the detection losses if training else returns the detections.
              The combined loss is the sum of the detection losses.
        
        Model training (see also `train_fasterrcnn`)
            - Phase 1: Train all layers (cache the proposals with `cache_phase1_proposals`).
            - Phase 2: Train all layers (with a new backbone, using the proposals from from phase 1).
            - Phase 3: Train only the RPN.
            - Phase 4: Train only the ROI heads.
            
        Model evaluation and testing
            - Phases 1, 2 and 3: Log only the proposal or detection losses and the combined loss.
            - Phase 4: Log the detection loss and the combined loss.
              Also, after every epoch compute and log detailed mAP and mAR results.
              Stop early if the the mAP doesn't improve.

        Args:
            num_classes (int): number of output classes of the model (including the background).
            lr (float, optional): learning rate to vbe used during training. Defaults to 1e-4.
            phase (Literal[1, 2, 3, 4], optional): The phase of the model. Should not be mutated. Defaults to 1.
            class_names (Optional[List[str]], optional): Names of the classes (excluding the background).
                If None then ['1', ..., '`num_classes`'] is used. Defaults to None.
        """

        super().__init__(num_classes, lr, class_names, phase=phase, **kwargs)
        
        self.model = get_fasterrcnn(num_classes=num_classes)
        self.phase = phase
        
        if self.phase == 1:
            self.model.roi_heads.requires_grad_(False)  # Not used
        elif self.phase == 2:
            self.model.rpn.requires_grad_(False)  # Not used
        elif self.phase == 3:
            self.model.backbone.requires_grad_(False)
            self.model.roi_heads.requires_grad_(False)  # Not used
        elif self.phase == 4:
            self.model.backbone.requires_grad_(False)
            self.model.rpn.requires_grad_(False)  # Not used

    def forward(
        self,
        images: List[Tensor],
        targets = None,
        cached_proposals: Optional[List[Tensor]] = None,
    ):
        """See also torchvision.models.detection.generalized_rcnn.GeneralizedRCNN.forward()"""
        image_list: ImageList
        original_image_sizes: List[Tuple[int, int]]
        features: Dict[str, Tensor]
        proposals: List[Tensor]

        transform: GeneralizedRCNNTransform = self.model.transform  # type: ignore
        backbone: BackboneWithFPN = self.model.backbone  # type: ignore
        rpn: RegionProposalNetwork = self.model.rpn  # type: ignore
        roi_heads: RoIHeads = self.model.roi_heads  # type: ignore

        # Forward
        image_list, targets = transform(images, targets)
        features = backbone(image_list.tensors)

        if self.phase in {1, 3, 4}:
            proposals, proposal_losses = rpn(image_list, features, targets)
        elif self.phase == 2:
            assert cached_proposals is not None
            proposals = cached_proposals

        if self.phase in {2, 4}:
            detections, detector_losses = roi_heads(
                features, proposals, image_list.image_sizes, targets
            )


        if self.phase in {1, 3} and self.training:
            return proposal_losses  # type: ignore
        elif self.phase in {2, 4} and self.training:
            return detector_losses  # type: ignore
        elif self.phase in {1, 3} and not self.training:
            return proposals  # type: ignore
        elif self.phase in {2, 4} and not self.training:
            original_image_sizes = [tuple(img.shape[-2:]) for img in images]
            detections = transform.postprocess(
                detections, image_list.image_sizes, original_image_sizes  # type: ignore
            )
            return detections

    def configure_optimizers(self):
        model = self.model

        if self.phase == 1:
            params = itertools.chain(
                model.backbone.parameters(), model.rpn.parameters()
            )
        elif self.phase == 2:
            params = itertools.chain(
                model.backbone.parameters(), model.roi_heads.parameters()
            )
        elif self.phase == 3:
            params = model.rpn.parameters()
        elif self.phase == 4:
            params = model.roi_heads.parameters()

        return Adam(params, lr=self.lr)

    def training_step(
        self, batch, batch_idx: int
    ) -> Tensor:
        if self.phase in {1,3,4}:
            assert len(batch) == 3
            _, images, targets = batch
            losses = self(images, targets)
        elif self.phase == 2:
            assert len(batch) == 4
            _, images, targets, cached_proposals = batch
            losses = self(images, targets, cached_proposals)

        loss = sum(losses.values())  # type: ignore
        self.log_dict({
            **{f'train_{k}': v for k, v in losses.items()},  # type: ignore
            **{'train_loss': loss}
        })

        return loss

    def shared_val_test_step(self, batch):

        if self.phase in {1,3}:
            raise ValueError(
                f'No validation or test step step for phase {self.phase}'
            )
        elif self.phase == 4:
            assert len(batch) == 3
            image_names, images, targets = batch
            detections = self(images)
        elif self.phase == 2:
            assert len(batch) == 4
            image_names, images, targets, cached_proposals = batch
            detections = self(images, cached_proposals=cached_proposals)

        return image_names, images, targets, detections


def cache_fasterrcnn(
    ckpt: str,
    loader: DataLoader,
    cache_dir,
    accelerator: str = 'cpu',
) -> None:
    images: List[Tensor]
    output: List[Tensor]
    model: LitFasterRCNN
    
    model = LitFasterRCNN.load_from_checkpoint(ckpt)
    print(f'Caching Faster R-CNN Phase {model.phase}')

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(exist_ok=True, parents=True)
    device = torch.device(accelerator if accelerator != 'gpu' else 'cuda')
    model.eval().to(device)

    for image_names, images, _ in tqdm(loader):
        images = [img.to(device) for img in images]
        with torch.inference_mode():
            output = model(images)
        for image_name, proposal in zip(image_names, output):
            torch.save(proposal.cpu(), cache_dir / f'{image_name}.pt')


class Phase2Dataset(ObjectsDataset):

    def __init__(
        self,
        root_dir,
        mode,
        proposals_dir, 
    ) -> None:
        """ObjectsDataset with proposals.
        No transform is used because proposals can lie outside the image bounds.
        """
        super().__init__(root_dir, mode, transform=None)
        self.proposals_dir = Path(proposals_dir)

        names = sorted(p.stem for p in self.proposals_dir.iterdir())
        if names != self.image_names:
            raise ValueError('Non matching proposal and image names.')

    def __getitem__(self, idx):
        image_name, image, targets = super().__getitem__(idx)
        proposals = torch.load(self.proposals_dir / f'{image_name}.pt')
        return image_name, image, targets, proposals
    
    @classmethod
    def from_objects_dataset(cls, dataset: ObjectsDataset, proposals_dir):
        return cls(dataset.root_dir, dataset.mode, proposals_dir)  # type: ignore


def _train_fasterrcnn_phase(
    phase,
    *,
    loader_train: DataLoader,
    output_dir,
    prev_ckpt: Optional[str] = None,
    num_classes: Optional[int] = None,
    loader_val: Optional[DataLoader] = None,
    loader_test: Optional[DataLoader] = None,
    lr: float = 1e-4,
    max_epochs: int = 10,
    accelerator: str = 'cpu',
    log_every_n_steps: int = 10,
    patience: int = 30,
    class_names: Optional[List[str]] = None
) -> str:
    """Train a Faster RCNN phase.
    
    `num_classes` is used only for phase 1.
    `ckpt` is used for phases 2, 3 and 4.
    `loader_val` and `loader_test` are used only for phase 4.
    
    Returns the path to the best model checkpoint saved during training.
    """

    print(f'Training Faster R-CNN Phase {phase}')

    # Model loading
    model: LitFasterRCNN

    if phase == 1:
        assert num_classes is not None
        model = LitFasterRCNN(
            num_classes=num_classes, lr=lr, phase=phase, class_names=class_names
        )
    elif phase == 2:
        assert prev_ckpt is not None
        model = LitFasterRCNN.load_from_checkpoint(prev_ckpt, lr=lr, phase=phase)
        model.model.backbone = get_fasterrcnn().backbone
    elif phase in {3, 4}:
        assert prev_ckpt is not None
        model = LitFasterRCNN.load_from_checkpoint(prev_ckpt, lr=lr, phase=phase)

    # Model Training
    default_root_dir = str(Path(output_dir, f'phase_{phase}'))

    if phase in {1,2,3}:
        trainer = pl.Trainer(
            default_root_dir=default_root_dir,
            callbacks=[
                ModelCheckpoint(monitor='train_loss', mode='min', save_weights_only=True),
            ],
            max_epochs=max_epochs,
            accelerator=accelerator,
            log_every_n_steps=log_every_n_steps,
        )
        trainer.fit(model, loader_train)
    elif phase == 4:
        assert loader_val is not None and loader_test is not None
        trainer = pl.Trainer(
            default_root_dir=default_root_dir,
            callbacks=[
                EarlyStopping(monitor='val_map', mode='max', patience=patience, verbose=True),
                ModelCheckpoint(monitor='val_map', mode='max'),
            ],
            max_epochs=max_epochs,
            accelerator=accelerator,
            log_every_n_steps=log_every_n_steps,
            val_check_interval=0.5
        )
        trainer.fit(model, loader_train, loader_val)
        trainer.test(ckpt_path='best', dataloaders=loader_test)

    new_ckpt: str = trainer.checkpoint_callback.best_model_path  # type: ignore
    return new_ckpt


def train_fasterrcnn(
    data_dir,
    output_dir,
    batch_size: int,
    accelerator: str,
    num_workers: int,
) -> str:
    print('Training Faster R-CNN')
    # Set up the datasets and dataloaders that are used in phases 1, 3 and 4.
    dataset_train_p134 = ObjectsDataset(data_dir, mode='train', transform=get_transform())
    dataset_val_p134 = ObjectsDataset(data_dir, mode='val')
    dataset_test_p134 = ObjectsDataset(data_dir, mode='test')
    dataset_cache_p1 = ObjectsDataset(data_dir, mode='train', transform=None)
    loader_train_p134, loader_val_p134, loader_test_p134 = create_dataloaders(
        dataset_train_p134,
        dataset_val_p134,
        dataset_test_p134,
        batch_size=batch_size,
        collate_fn=transpose,
        num_workers=num_workers,
    )
    loader_cache_p1 = DataLoader(
        dataset_cache_p1,
        batch_size=batch_size,
        collate_fn=transpose,
        num_workers=num_workers,
        shuffle=False
    )
    fasterrcnn_dir = Path(output_dir, 'fasterrcnn')
    class_names = ObjectsDataset.class_names
    num_classes = 1 + len(class_names)  # Including background

    # Train phase 1 and cache the proposals.
    ckpt1 = _train_fasterrcnn_phase(
        phase=1,
        output_dir=fasterrcnn_dir,
        loader_train=loader_train_p134,
        num_classes=num_classes,
        accelerator=accelerator,
        lr=1e-4,
        max_epochs=20,
        class_names=class_names,
    )
    proposals_dir = Path(ckpt1).parent.parent / 'proposals_cache'  # version_{i} / 'proposals_cache'
    cache_fasterrcnn(ckpt1, loader_cache_p1, proposals_dir, accelerator=accelerator)

    # Set up the dataset and loader that is used in phase 2.
    dataset_train_p2 = Phase2Dataset.from_objects_dataset(dataset_cache_p1, proposals_dir)
    loader_train_p2 = DataLoader(
        dataset_train_p2,
        batch_size=batch_size,
        collate_fn=transpose,
        num_workers=num_workers,
        shuffle=True
    )
    
    # Train phases 2, 3 and 4, and return the best phase 4 model checkpoint path.
    ckpt2 = _train_fasterrcnn_phase(
        phase=2,
        output_dir=fasterrcnn_dir,
        prev_ckpt=ckpt1,
        loader_train=loader_train_p2,
        accelerator=accelerator,
        lr=1e-4,
        max_epochs=20,
    )
    ckpt3 = _train_fasterrcnn_phase(
        phase=3,
        output_dir=fasterrcnn_dir,
        prev_ckpt=ckpt2,
        loader_train=loader_train_p134,
        accelerator=accelerator,
        lr=1e-4,
        max_epochs=20,
    )
    ckpt4 = _train_fasterrcnn_phase(
        phase=4,
        output_dir=fasterrcnn_dir,
        prev_ckpt=ckpt3,
        loader_train=loader_train_p134,
        loader_val=loader_val_p134,
        loader_test=loader_test_p134,
        accelerator=accelerator,
        lr=1e-4,
        max_epochs=50,
    )
    return ckpt4


def main():
    # Setup
    pl.seed_everything(42)
    data_dir = Path('../input/object-detection-batteries-dices-and-toy-cars/dataset/dataset')
    output_dir = Path('output')
    accelerator = 'gpu' if torch.cuda.is_available() else 'cpu'

    retinanet_ckpt = train_retinanet(
        data_dir,
        output_dir,
        batch_size=4,
        accelerator=accelerator,
        num_workers=2,
    )
    
    fasterrcnn_ckpt = train_fasterrcnn(
        data_dir,
        output_dir,
        batch_size=4,
        accelerator=accelerator,
        num_workers=2,
    )


main()
