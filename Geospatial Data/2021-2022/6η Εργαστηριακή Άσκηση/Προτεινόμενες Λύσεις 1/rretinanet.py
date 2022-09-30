_base_ = './configs/rotated_retinanet/rotated_retinanet_obb_r50_fpn_1x_dota_le90.py'

data_root = './data/split_ss_dota/'
data = dict(
    samples_per_gpu=3,  # 1 if low on GPU memory
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
