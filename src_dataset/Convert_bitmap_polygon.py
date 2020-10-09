"""
bitmap形式のファイルを入力し、各時間ごとのPolygonのPickleファイルを出力するプログラム
実行例:/opt/anaconda3/envs/py3.7/bin/python /Users/komatsu/Documents/Predict_Solar_Flare_Mrcnn/src_dataset/Convert_bitmap_polygon.py "/Users/komatsu/Documents/Predict_Solar_Flare_Mrcnn/samples/sun/Mharp/hmi.Mharp_720s.1.20100501_0*_TAI.bitmap.fits" --pickle_path "/Users/komatsu/Documents/Predict_Solar_Flare_Mrcnn/src_dataset/coord_df.pickle"
"""

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
import argparse
import utils
import pickle
from tqdm import tqdm
from dateutil.relativedelta import relativedelta
FULL_DISK_COORD = 4096

parser = argparse.ArgumentParser()
parser.add_argument("input_mask_path")
parser.add_argument("input_flare_table_path")
args = parser.parse_args()
def main():
    mask_paths_string = args.input_mask_path
    mask_paths = sorted(glob.glob(mask_paths_string))
    flare_df_paths_string = args.input_flare_table_path
    flare_df_paths = sorted(glob.glob(flare_df_paths_string))
    flare_df_paths_dic = {path.split("/")[-1][:-4]:path for path in flare_df_paths}
    start = dt.strptime(mask_paths[0].split(".")[-3], "%Y%m%d_%H%M%S_TAI")
    start = start.replace(day=1,hour=0)
    end =start+relativedelta(months=1)
    coord_df = initialize_df(start,end)
    # print(mask_paths)
    for mask_path in tqdm(mask_paths,desc ="{}-{}".format(start,end)):
        mask_map = sunpy.map.Map(mask_path)
        ar_num=mask_path.split(".")[-4]
        flare_df = pd.read_table(flare_df_paths_dic[str(ar_num)])
        flare_df["Timestamp"] = pd.to_datetime(flare_df["Timestamp"])
        # print(flare_df)
        flare_df.set_index("Timestamp",inplace = True)
        # print(flare_df)
        rec_datetime = dt.strptime(mask_map.meta["t_rec"][:-4],"%Y.%m.%d_%H:%M:%S")
        # print(flare_df.loc[rec_datetime])# 時間以上の精度で参照するときは.loc関数を使用する
        mask_map = sunpy.map.Map(mask_path)
        padded_mask_map = padding_mask(mask_map)
        # print(padded_mask_map.shape)
        if (padded_mask_map.shape == (0,0)):
            print("error : continue")
            print(mask_path)
            continue
        rotated_padded_mask_map = rotate_map(mask_map, padded_mask_map)
        # utils.compare_map(padded_mask_map,rotated_padded_mask_map)
        # exit()
        ar_polygon = polygonize_map(mask_map, rotated_padded_mask_map)
        # print("ar_polygon:",ar_polygon)
        # utils.show_polygon(ar_polygon[0])
        # tqdm.write("now:{}".format(len(ar_polygon)))
        # 一つのSHARPデータの中に複数のPolygonが入っていた場合を考慮
        if (len(ar_polygon)==1):
            if(len(ar_polygon[0])!=2):
                # print("len1_T",mask_path,len(ar_polygon[0]))
                coord_df.loc[rec_datetime]["Polygon"].append(ar_polygon[0])
                add_flare_label(coord_df,flare_df,rec_datetime)
            else:
                # print("len1_F",mask_path,len(ar_polygon))
                coord_df.loc[rec_datetime]["Polygon"].append(ar_polygon)
                add_flare_label(coord_df,flare_df,rec_datetime)
        elif(len(ar_polygon)==0):
            pass
        else:
            for polygon in ar_polygon:
                if(len(polygon[0])!=2):
                        # print("len2_T",mask_path,len(polygon[0]))
                        coord_df.loc[rec_datetime]["Polygon"].append(polygon[0])
                        add_flare_label(coord_df,flare_df,rec_datetime)
                else:
                        # print("len2_F",mask_path,len(polygon))
                        coord_df.loc[rec_datetime]["Polygon"].append(polygon)
                        add_flare_label(coord_df,flare_df,rec_datetime)
        # tqdm.write("sum:{}".format(len(coord_df.loc[rec_datetime]["Polygon"])))
        # utils.show_polygons(ar_polygon)
        # print(coord_df[rec_datetime])
    coord_df.to_pickle("../coord_dfs/{}{}coord_df.pickle".format(start.year,str(start.month).zfill(2)))

    

def padding_mask(mask_map):
    binarized_mask_map=np.where((mask_map.data==33)|(mask_map.data==34),1,0)
    mask_center = np.array([mask_map.reference_pixel[0].value,mask_map.reference_pixel[1].value])
    mask_ll = mask_center-(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    mask_ur = mask_center+(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    full_disk_coord = 4096
    pad_width = np.array([[full_disk_coord-mask_ur[1],mask_ll[1]],[mask_ll[0],full_disk_coord-mask_ur[0]]])
    try:
        padded_mask_map = np.pad(np.flipud(binarized_mask_map),np.array(pad_width,dtype="int"),"constant")
    except ValueError:
        tqdm.write("error occured")
        tqdm.write(mask_center,mask_ll,mask_ur)
        padded_mask_map = np.ndarray([0,0])
    return padded_mask_map

def rotate_map(mask_map,padded_mask_map):
    height = FULL_DISK_COORD
    width = FULL_DISK_COORD
    center = (mask_map.meta["imcrpix1"],mask_map.meta["imcrpix2"])
    angle = -1* mask_map.meta["crota2"]
    scale = 1.0
    trans = cv2.getRotationMatrix2D(center,angle,scale)
    rotated_padded_mask_map = cv2.warpAffine(padded_mask_map.astype("int16"),trans,(width,height))
    rotated_padded_mask_map = np.flipud(rotated_padded_mask_map)
    return rotated_padded_mask_map

def polygonize_map(mask_map,rotated_padded_mask_map):
    mask_center = np.array([mask_map.reference_pixel[0].value,mask_map.reference_pixel[1].value])
    mask_ll = mask_center-(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    mask_ur = mask_center+(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    # print("coord:",mask_center,mask_ll,mask_ur)
    left = int(FULL_DISK_COORD-mask_ur[0])
    right = int(FULL_DISK_COORD-mask_ll[0])
    lower = int(FULL_DISK_COORD-mask_ur[1])
    upper = int(FULL_DISK_COORD-mask_ll[1])
    # print("rotated_coord:",left,right,lower,upper)
    # exit()
    rotated_ar_mask_map = rotated_padded_mask_map[lower:upper,left:right]
    ar_polygons =[]
    ar_polygon_gen = shapes(rotated_ar_mask_map.astype("int16"),mask=None,connectivity = 8)
    for i,polygon in enumerate(ar_polygon_gen):
        # print(i,"\n")
        # print(polygon[0]["coordinates"][0])
        if(polygon[0]["coordinates"][0][0]!=(0.0,0.0)):
            points = [(point[0]+left,point[1]+lower)for point in polygon[0]["coordinates"][0]]
            # print("Points",points)
            ar_polygons.append(points)
    # print("len(ar_polygons)",len(ar_polygons))
    return ar_polygons

def initialize_df (start,end):
    time_index = pd.date_range(start = start,end = end,freq ="H")
    time_df = pd.DataFrame([[[],[],[],[]] for i in range(len(time_index))],index = time_index,columns =["Polygon","C_FLARE","M_FLARE","X_FLARE"])
    return time_df

def add_flare_label(coord_df,flare_df,rec_datetime):
    if (flare_df.loc[rec_datetime]["CFLARE_LABEL_LOC"]!="None"):
        tqdm.write(flare_df.loc[rec_datetime]["CFLARE_LABEL_LOC"])
        coord_df.loc[rec_datetime]["C_FLARE"].append(flare_df.loc[rec_datetime]["CFLARE_LABEL_LOC"])
    else:
        coord_df.loc[rec_datetime]["C_FLARE"].append(0)
    if (flare_df.loc[rec_datetime]["MFLARE_LABEL_LOC"]!="None"):
        tqdm.write(flare_df.loc[rec_datetime]["MFLARE_LABEL_LOC"])
        coord_df.loc[rec_datetime]["M_FLARE"].append(flare_df.loc[rec_datetime]["MFLARE_LABEL_LOC"])
    else:
        coord_df.loc[rec_datetime]["M_FLARE"].append(0)
    if (flare_df.loc[rec_datetime]["XFLARE_LABEL_LOC"]!="None"):
        tqdm.write(flare_df.loc[rec_datetime]["XFLARE_LABEL_LOC"])
        coord_df.loc[rec_datetime]["X_FLARE"].append(flare_df.loc[rec_datetime]["XFLARE_LABEL_LOC"])
def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)
def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data

main()