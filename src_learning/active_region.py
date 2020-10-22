"""
Mask R-CNN学習用スクリプト
ex)python3 active_region.py train --dataset /home/jovyan/dataset/dataset/HMI_REGION/ --model imagenet
"""

import os
import sys
import time
import numpy as np
import imgaug

ROOT_DIR = os.path.abspath("/home/maskr-cnn")
print(ROOT_DIR)
sys.path.append(ROOT_DIR)

from mrcnn.config import Config
from mrcnn import model as modellib, utils

DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
from pycocotools.coco import COCO

# Path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

class SunConfig(Config):
    # 太陽データを使用して学習するに当たって変更すべきConfigを変更
    # Give the configuration a recognizable name
    NAME = "sun"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 2  # ARorQRの2通り＋Background


class SunDataset(utils.Dataset):
    def load_coco(self, dataset_dir, class_ids=None,class_map=None, return_coco=False):
        coco = COCO("{}/annotations/dataset.json".format(dataset_dir))
        image_dir = str(dataset_dir)

        if return_coco:
            return coco

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

        # Configurations
    if args.command == "train":
        config = SunConfig()
    else:
        class InferenceConfig(SunConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 2
            DETECTION_MIN_CONFIDENCE = 0
        config = InferenceConfig()
    config.display()
        # Create model
    if args.command == "train":
        model = modellib.MaskRCNN(mode="training", config=config,
                                  model_dir=args.logs)
    else:
        model = modellib.MaskRCNN(mode="inference", config=config,
                                  model_dir=args.logs)
    
    # Select weights file to load
    if args.model.lower() == "coco":
        model_path = COCO_MODEL_PATH
    elif args.model.lower() == "last":
        # Find last trained weights
        model_path = model.find_last()
    elif args.model.lower() == "imagenet":
        # Start from ImageNet trained weights
        model_path = model.get_imagenet_weights()
    else:
        model_path = args.model

    # Load weights 
    print("Loading weights ", model_path)
    model.load_weights(model_path, by_name=True)

    if args.command == "train":
        # Training dataset. Use the training set and 35K from the
        # validation set, as as in the Mask RCNN paper.
        # dataset_train = SunDataset()
        pass