"""
Mask R-CNN学習用スクリプト
ex)python3 active_region.py train --dataset /home/jovyan/dataset/dataset/HMI_REGION/ --model imagenet
"""

import os
import sys
import time
import numpy as np
import imgaug

ROOT_DIR = os.path.abspath("/home/jovyan/maskr-cnn")
print(ROOT_DIR)
sys.path.append(ROOT_DIR)

from mrcnn.config import Config
from mrcnn import model as modellib, utils

DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
from pycocotools.coco import COCO

class SunConfig(Config):
    # 太陽データを使用して学習するに当たって変更すべきConfigを変更
    # Give the configuration a recognizable name
    NAME = "sun"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1


    # Number of classes (including background)
    NUM_CLASSES = 1 + 2  # ARorQRの2通り＋Background


class SunDataset(utils.Dataset):
    pass

if __name__ == '__main__':
    import argparse
        # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Train Mask R-CNN on MS COCO.')
    parser.add_argument("command",
                        metavar="<command>",
                        help="'train' or 'evaluate' on MS COCO")
    parser.add_argument('--dataset', required=True,
                        metavar="/path/to/coco/",
                        help='Directory of the MS-COCO dataset')
    parser.add_argument('--model', required=True,
                        metavar="/path/to/weights.h5",
                        help="Path to weights .h5 file or 'coco'")
    parser.add_argument('--logs', required=False,
                        default=DEFAULT_LOGS_DIR,
                        metavar="/path/to/logs/",
                        help='Logs and checkpoints directory (default=logs/)')
    parser.add_argument('--limit', required=False,
                        default=500,
                        metavar="<image count>",
                        help='Images to use for evaluation (default=500)')
    args = parser.parse_args()
    print("Command: ", args.command)
    print("Model: ", args.model)
    print("Dataset: ", args.dataset)
    print("Logs: ", args.logs)