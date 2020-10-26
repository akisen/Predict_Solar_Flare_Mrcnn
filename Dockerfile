FROM nvidia/cuda:8.0-cudnn6-devel-ubuntu16.04
USER root
RUN apt-get update && \
    apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-dev &&\
    apt-get update &&\
    apt-get install -y git &&\
    apt-get install -y --allow-unauthenticated graphviz &&\
    apt install -y curl
RUN apt-get install -y python3 python3-pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py
COPY requirements.txt ${PWD}
RUN pip3 install -r requirements.txt
RUN pip3 install pycocotools
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all