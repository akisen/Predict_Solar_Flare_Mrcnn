from glob import glob
import sunpy.map
import cv2
import astropy.units as u
import sys
import argparse
from tqdm import tqdm
import warnings
warnings.simplefilter('ignore')
parser = argparse.ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
parser.add_argument("--format",default="datetime",type=str)
FULL_DISK_COORD = 4096
args = parser.parse_args()
input_path = args.input_path
paths = sorted(glob(input_path))
# print(paths)
for i, path in enumerate(tqdm(paths)):
    if(args.format == "number"):
        filename=str(args.output_path)+str(i).zfill(3)+".jpg"
    else:
        filename=str(args.output_path)+path.split(".")[2][0:15]+".jpg"
    map=sunpy.map.Map(path)
    height = FULL_DISK_COORD
    width = FULL_DISK_COORD
    center = (map.meta["crpix1"],map.meta["crpix2"])
    angle = -1* map.meta["crota2"]
    scale = 1.0
    trans = cv2.getRotationMatrix2D(center,angle,scale)
    rotated_map = cv2.warpAffine(map.data.astype("int16"),trans,(width,height))
    # print(filename)
    cv2.imwrite(filename,rotated_map)