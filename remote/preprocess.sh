#!/bin/sh
cd /home/akito/Documents/Predict_Solar_Flare_Mrcnn/src_dataset
python3 auto_convert_bitmap_to_polygon.py
python3 auto_make_coco.py