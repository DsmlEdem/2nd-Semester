from pathlib import Path
import argparse

from mmdet.apis.inference import show_result_pyplot
from mmcv.runner import load_checkpoint
from mmrotate.apis.inference import inference_detector_by_patches
from mmrotate.datasets.builder import build_dataset
from mmrotate.models import build_detector
from mmcv.utils.config import Config


def visualize_predictions(config_path, checkpoint_path, imagedir, outdir=None):
    
    if outdir is not None:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=False)
    
    config = Config.fromfile(config_path)
    
    dataset = build_dataset(config.data.train)
    classes = dataset.CLASSES
    palette = dataset.PALETTE
    
    model = build_detector(config.model)
    load_checkpoint(model, checkpoint_path)
    model.cfg = config  # `inference_detector_by_patches` requires it for `model.cfg.data.test.pipeline`
    model.CLASSES = classes
    model.to(config.device)
    model.eval()

    for image_path in sorted(Path(imagedir).iterdir()):
        dets = inference_detector_by_patches(
            model=model, img=image_path, sizes=[1024], steps=[824], ratios=[0.5, 1.0, 2.0], merge_iou_thr=0.1
        )
        outfile = outdir / f'{image_path.stem}_pred{image_path.suffix}' if outdir is not None else None
        show_result_pyplot(model, image_path, dets, score_thr=0.4, palette=palette, out_file=outfile)


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize predictions of a model on the DOTA Dataset.")
    parser.add_argument('--config', help="The configuration used for training the model.")
    parser.add_argument('--checkpoint', help="The checkpoint to use for loading the model.")
    parser.add_argument('--imagedir', help="The directory containing the DOTA images.")
    parser.add_argument('--outdir', help="The outputs directory. If not specified plt.show() will be used.")
    args = parser.parse_args()
    return args 


def main():
    args = parse_args()
    visualize_predictions(args.config, args.checkpoint, args.imagedir, args.outdir)
    
    
if __name__ == '__main__':
    main()
