import sunpy.map
import astropy.units as u
import glob
import matplotlib.pyplot as plt
import matplotlib.patches as pat
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
import cv2
from datetime import datetime as dt
import sys

import utils

FULL_DISK_COORD = 4096
START = "2010-05-01"
END = "2010-05-31"
args = sys.argv
def main():
    coord_series = initialize_series()
    # print(args[1])
  
    mask_paths_string = args[1]
    # print(mask_paths_string)
    mask_paths = sorted(glob.glob(mask_paths_string))
    # print(mask_paths)
    for mask_path in mask_paths:
        print(mask_path)
        # print(mask_path)
        mask_map = sunpy.map.Map(mask_path)
        padded_mask_map = padding_mask(mask_map)
        rotated_padded_mask_map = rotate_map(mask_map, padded_mask_map)
        # utils.compare_map(padded_mask_map,rotated_padded_mask_map)
        # exit()
        ar_polygon = polygonize_map(mask_map, rotated_padded_mask_map)
        rec_datetime = dt.strptime(mask_map.meta["t_rec"][:-4],"%Y.%m.%d_%H:%M:%S")
        print("now:",len(ar_polygon))
        # 一つのSHARPデータの中に複数のPolygonが入っていた場合を考慮
        if (len(ar_polygon)==1):
            # print(ar_polygon[0])
            coord_series[rec_datetime].append(ar_polygon[0])
        elif(len(ar_polygon)==0):
            pass
        else:
            for polygon in ar_polygon:
                print(mask_path,polygon[0])
                coord_series[rec_datetime].append(polygon[0])
        print("sum:",len(coord_series[rec_datetime]))
        # utils.show_polygons(ar_polygon)
        utils.pickle_dump(coord_series,"/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/src_dataset/Coord_series.pickle")
    

def padding_mask(mask_map):
    binarized_mask_map=np.where((mask_map.data==33)|(mask_map.data==34),1,0)
    mask_center = np.array([mask_map.reference_pixel[0].value,mask_map.reference_pixel[1].value])
    mask_ll = mask_center-(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    mask_ur = mask_center+(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    pad_width = np.array([[FULL_DISK_COORD-mask_ur[1],mask_ll[1]],[mask_ll[0],FULL_DISK_COORD-mask_ur[0]]])
    padded_mask_map = np.pad(binarized_mask_map,np.array(pad_width,dtype="int"),"constant")
    return padded_mask_map
def rotate_map(mask_map,padded_mask_map):
    height = FULL_DISK_COORD
    width = FULL_DISK_COORD
    center = (mask_map.meta["imcrpix1"],mask_map.meta["imcrpix2"])
    angle = -1* mask_map.meta["crota2"]
    scale = 1.0
    trans = cv2.getRotationMatrix2D(center,angle,scale)
    rotated_padded_mask_map = cv2.warpAffine(padded_mask_map.astype("int16"),trans,(width,height))
    return rotated_padded_mask_map
def polygonize_map(mask_map,rotated_padded_mask_map):
    mask_center = np.array([mask_map.reference_pixel[0].value,mask_map.reference_pixel[1].value])
    mask_ll = mask_center-(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    mask_ur = mask_center+(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    left = int(FULL_DISK_COORD-mask_ur[0])
    right = int(FULL_DISK_COORD-mask_ll[0])
    lower = int(mask_ll[1])
    upper = int(mask_ur[1])
    rotated_ar_mask_map = rotated_padded_mask_map[lower:upper,left:right]
    ar_polygons =[]
    ar_polygon_gen = shapes(rotated_ar_mask_map.astype("int16"),mask=None,connectivity = 8)
    for i,polygon in enumerate(ar_polygon_gen):
        # print(i,"\n")
        # print(polygon[0]["coordinates"][0])
        points = [(point[0]+left,point[1]+right)for point in polygon[0]["coordinates"][0]]
        ar_polygons.append(points)
    # print(len(ar_polygons))
    return ar_polygons[:-1]
def initialize_series ():
    time_index = pd.date_range(start = START,end = END,freq ="H")
    time_series = pd.Series([[] for i in range(len(time_index))],index = time_index)

    return time_series



main()