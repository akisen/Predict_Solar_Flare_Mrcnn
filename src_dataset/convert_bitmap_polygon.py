"""
bitmap形式のファイルを入力し、各時間ごとのPolygonのPickleファイルを出力するプログラム
実行例: 'python3 convert_bitmap_polygon.py "/media/akito/Data21/hmi.Mharp_720s/{0}/{0}{1}/*.fits" "/media/akito/Data5/SWAN_Flare/dataverse_files/SWAN/*/*"
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
from shapely.geometry import Polygon
from shapely.wkt import loads as load_wkt
FULL_DISK_COORD = 4096

parser = argparse.ArgumentParser()
parser.add_argument("input_mask_path")
parser.add_argument("input_flare_table_path")
parser.add_argument("output_path")
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

    for mask_path in tqdm(mask_paths,desc ="{}-{}".format(start,end)):
        mask_map = sunpy.map.Map(mask_path)
        ar_num=mask_path.split(".")[-4]
        flare_df = pd.read_csv(flare_df_paths_dic[str(ar_num)],index_col=0)
        rec_datetime = dt.strptime(mask_map.meta["t_rec"][:-4],"%Y.%m.%d_%H:%M:%S")
        # print(flare_df.loc[rec_datetime])# 時間以上の精度で参照するときは.loc関数を使用する
        mask_map = sunpy.map.Map(mask_path)
        padded_mask_map = padding_mask(mask_map)
        if (padded_mask_map.shape == (0,0)):
            tqdm.write("error : continue")
            tqdm.write(mask_path)
            continue
        rotated_padded_mask_map = rotate_map(mask_map, padded_mask_map)
        ar_polygon = polygonize_map(mask_map)
        # 一つのSHARPデータの中に複数のPolygonが入っていた場合を考慮
        if (len(ar_polygon)==1):
            if(len(ar_polygon[0])!=2):
                coord_df.loc[rec_datetime]["Polygon"].append(ar_polygon[0])
                add_flare_label(coord_df,flare_df,rec_datetime)
            else:
                coord_df.loc[rec_datetime]["Polygon"].append(ar_polygon)
                add_flare_label(coord_df,flare_df,rec_datetime)
        elif(len(ar_polygon)==0):
            pass
        else:
            for polygon in ar_polygon:
                if(len(polygon[0])!=2):
                        coord_df.loc[rec_datetime]["Polygon"].append(polygon[0])
                        add_flare_label(coord_df,flare_df,rec_datetime)
                else:
                        coord_df.loc[rec_datetime]["Polygon"].append(polygon)
                        add_flare_label(coord_df,flare_df,rec_datetime)
    coord_df.to_pickle("{}/{}{}coord_df.pickle".format(args.output_path,start.year,str(start.month).zfill(2)))

    

def padding_mask(mask_map):
    binarized_mask_map=np.where((mask_map.data==33)|(mask_map.data==34),1,0)
    mask_center = np.array([mask_map.reference_pixel[0].value,mask_map.reference_pixel[1].value])
    mask_ll = mask_center-(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    mask_ur = mask_center+(mask_map.meta["naxis1"]//2,mask_map.meta["naxis2"]//2)
    full_disk_coord = 4096
    pad_width = np.array([[full_disk_coord-mask_ur[1],mask_ll[1]],[mask_ll[0],full_disk_coord-mask_ur[0]]])
    if(mask_ll[0]>=0 and mask_ll[1]>=0):
        padded_mask_map = np.pad(np.flipud(binarized_mask_map),np.array(pad_width,dtype="int"),"constant")
    else:
        # tqdm.write("{}{}{}".format(mask_center,mask_ll,mask_ur))
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

def polygonize_map(mask_map):
    binarized_mask_map=np.where((mask_map.data==33)|(mask_map.data==34),1,0)
    ll_x = mask_map.meta["crpix1"]
    ll_y = mask_map.meta["crpix2"]
    ar_polygons =[]
    ar_polygon_gen = shapes(binarized_mask_map.astype("int16"),mask=None,connectivity = 8)
    for ar_polygon in ar_polygon_gen:
        if(ar_polygon[0]["coordinates"][0][0]!=(0.0,0.0)):
            poly = [[coord[0]+ll_x,coord[1]+ll_y] for coord in ar_polygon[0]["coordinates"][0]]
            poly_txt = ["{} {}".format(coord[0]+ll_x,coord[1]+ll_y) for coord in ar_polygon[0]["coordinates"][0]]
            poly_txt = ",".join(poly_txt)
            poly_txt = "POLYGON(("+poly_txt+"))" # wktの入力Formatに調整
            # polygon = Polygon(poly)
            polygon_wkt = load_wkt(poly_txt)
            centroid = polygon_wkt.centroid.wkt # 重心の導出
            c_x = centroid.split(" ")[1][1:]
            c_y = centroid.split(" ")[2][:-1]
            poly = expand_polygon(poly,2, c_x, c_y)
            ar_polygons.append(poly)
    return ar_polygons

def expand_polygon (polygon,expand,c_x,c_y):
    for point in polygon:
        if point[0]< float(c_x):
            point[0] -= expand
        else:
            point[0] += expand
        if point[1] < float(c_y):
            point[1] -= expand
        else:
            point[1] += expand
    return polygon
def initialize_df (start,end):
    time_index = pd.date_range(start = start,end = end,freq ="H")
    time_df = pd.DataFrame([[[],[],[],[]] for i in range(len(time_index))],index = time_index,columns =["Polygon","C_FLARE","M_FLARE","X_FLARE"])
    return time_df

def add_flare_label(coord_df,flare_df,rec_datetime):
    rec_datetime = rec_datetime
    with open("../logs/{}{}.txt".format(rec_datetime.year,str(rec_datetime.month).zfill(2)),mode="a") as f:
        if (is_flared(rec_datetime,24,flare_df,"C")):
            label = is_flared(rec_datetime,24,flare_df,"C")
            tqdm.write(label)
            coord_df.loc[rec_datetime]["C_FLARE"].append(label)
            f.write("{}:{}\n".format(rec_datetime,label))
        else:
            coord_df.loc[rec_datetime]["C_FLARE"].append(0)
        if (is_flared(rec_datetime,24,flare_df,"M")):
            label = is_flared(rec_datetime,24,flare_df,"M")
            tqdm.write(label)
            coord_df.loc[rec_datetime]["M_FLARE"].append(label)
            f.write("{}:{}\n".format(rec_datetime,label))
        else:
            coord_df.loc[rec_datetime]["M_FLARE"].append(0)
        if (is_flared(rec_datetime,24,flare_df,"X")):
            label = is_flared(rec_datetime,24,flare_df,"X")
            tqdm.write(label)
            coord_df.loc[rec_datetime]["X_FLARE"].append(label)
            f.write("{}:{}\n".format(rec_datetime,label))
        else:
            coord_df.loc[rec_datetime]["X_FLARE"].append(0)
def is_flared (rec_datetime,span,flare_df,flare_class):
    for _ in range (span):
        rec_datetime = rec_datetime+ relativedelta(hours=1)
        key = flare_class+"FLARE_LABEL_LOC"
        if(rec_datetime in flare_df.index):
            if(flare_df.loc[rec_datetime][key]!="None"):
                return flare_df.loc[rec_datetime][key]
    return False
def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj,f)

def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data


main()