from glob import glob
import sunpy.map
import cv2
import astropy.units as u
import sys
import argparse
from tqdm import tqdm
import warnings
import numpy as np
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
    data = np.where(map.data<-2000,-2000,map.data)
    data = np.where(data>2000,2000,data)
    data = data+2000
    data = data/(4000/255)
    data = np.nan_to_num(data)

    print(data.min(),data.max())
    cv2.imwrite(filename,data)