FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-devel

# NVIDIA Fix: https://developer.nvidia.com/blog/updating-the-cuda-linux-gpg-repository-key/
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub \
    && apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub \
    && apt update \
    && apt install -y ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 tree zip unzip wget \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install \
    mmcv-full==1.6.0 -f https://download.openmmlab.com/mmcv/dist/cu113/torch1.11.0/index.html \
    mmengine==0.1.0 \
    shapely==1.8.4 \
    tensorboard==2.10.0 \
    jupyter==1.0.0

RUN pip install mmdet==2.25.1

RUN git clone https://github.com/open-mmlab/mmrotate.git
WORKDIR mmrotate
RUN git checkout tags/v0.3.2 \
    && pip install -v -e . \
    && echo "data/" >> .gitignore && echo "work_dirs/" >> .gitignore

# For matplotlib. https://stackoverflow.com/a/51881727/17386164
ARG DEBIAN_FRONTEND=noninteractive
ARG DEBCONF_NONINTERACTIVE_SEEN=true
RUN echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections \
    && echo 'tzdata tzdata/Zones/Etc select Athens' | debconf-set-selections \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends python3-tk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
 