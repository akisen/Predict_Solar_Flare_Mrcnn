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
    cv2.imwrite(filename,map.data)