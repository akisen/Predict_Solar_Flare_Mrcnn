from glob import glob
import sunpy.map
import cv2
import astropy.units as u
import sys
import argparse
from tqdm import tqdm
import warnings
import numpy as np
import  pathlib
from multiprocessing import Pool
warnings.simplefilter('ignore')
parser = argparse.ArgumentParser()
parser.add_argument("input_path")
parser.add_argument("output_path")
parser.add_argument("--format",default="datetime",type=str)
parser.add_argument("--channel",default=1,type=int)
FULL_DISK_COORD = 4096
args = parser.parse_args()
input_path = args.input_path
# print(paths)


def main():
    if(args.channel == 1):
        convert_map_1chanel(input_path)
    elif(args.channel == 3):
        convert_map_3chanels(input_path)
# TODO debug convert_map_1chanel
def convert_map_1chanel(input_path):
    paths = sorted(glob(input_path))
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

    # print(data.min(),data.max())
    cv2.imwrite(filename,data)

def convert_map_3chanels(input_path):
    # TODO add method  to support for 3channels
    azimuth_paths = glob(input_path+"*azimuth.fits")
    # for i, path in enumerate(tqdm(azimuth_paths)):
    #     stack_maps(path)
    with Pool(6) as pool:
        imap = pool.imap(stack_maps,azimuth_paths)
        result = list(tqdm(imap,total=len(azimuth_paths)))

def stack_maps(path):
    field_path = pathlib.Path(path.replace("azimuth","field"))
    inclination_path = pathlib.Path(path.replace("azimuth","inclination"))
    filename=str(args.output_path)+path.split(".")[3][0:15]+".jpg"
    if(field_path.exists() and inclination_path.exists()):
        azimath_map=sunpy.map.Map(path)
        field_map = sunpy.map.Map(field_path)
        inclination_map = sunpy.map.Map(inclination_path)
        data = np.stack([azimath_map.data,field_map.data,inclination_map.data],axis=-1)
        data = np.where(data>2000,2000,data)
        data = data+2000
        data = data/(4000/255)
        data = np.nan_to_num(data)
        cv2.imwrite(filename,data)
main()