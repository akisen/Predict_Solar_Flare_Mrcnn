import json
import collections as cl
import argparse
import sunpy.map
import glob
import pickle
import pandas as pd
from tqdm import tqdm
import itertools
from shapely.geometry import Polygon
import utils
import os
def info():
    tmp = cl.OrderedDict() # OrderedDict:値を追加した順序を記憶することができる辞書型風のデータ構造を提供
    tmp["descripion"] = "Predicting_Solar_Flare"
    tmp["version"] = "0.1"
    tmp["year"] = 2020
    tmp["contributor"] = "Akito Komatsu"
    tmp["data_created"] = "2020/10/01"
    return tmp

def images(coord_df):
    tmps =[]
    indexs = [index.strftime("%Y%m%d%H%M%S") for index in coord_df.index]
    for index in indexs:
        filename =  "{}_{}.jpg".format(index[0:8],index[8:])
        if (os.path.exists("/media/akito/Data21/Experiments/201005_1107_shuffle/train_figs/"+filename)):
            # print(len(coord_df.loc[index,"C_FLARE"].values[0]))
            tmp = cl.OrderedDict()
            tmp ["file_name"] = filename
            tmp["height"] = 4096
            tmp["width"] = 4096
            tmp["date_captured"] = index
            tmp["id"] = index[2:10]
            tmps.append(tmp)
            tqdm.write(str(tmp))
    return tmps

def annotations(coord_df):
    tmps = []
    coord_df = coord_df.apply(make_annotation_line,tmp=tmps,axis=1)
    # annotations = [annotation for annotation in series for series in coord_df]
    annotations = [coord_df.iloc[i][j]for i in range(len(coord_df)) for j in range(len(coord_df[i]) )]
    return annotations

def make_annotation_line(line,tmp):
    tmps = []
    for i in range(len(line["Polygon"])):
        tmp = cl.OrderedDict()
        polygon = Polygon(line["Polygon"][i])
        tmp["segmentation"] = [list(itertools.chain.from_iterable(line["Polygon"][i]))]
        tmp["area"] = polygon.area
        tmp["iscrowd"] = 0
        image_id = line.name.strftime("%Y%m%d%H%M%S")
        image_id = image_id[2:10]
        tmp["image_id"] = image_id
        tmp["id"] = ("{}{}".format(image_id,i+1))
        bb_coord = polygon.bounds
        bbox = [bb_coord[0],bb_coord[1],bb_coord[2]-bb_coord[0],bb_coord[3]-bb_coord[1]]
        tmp["bbox"] = bbox
        try:
            if(line["C_FLARE"][i]!=0 or line["M_FLARE"][i]!=0 or line["M_FLARE"][i]!=0 ):
                tmp["category_id"] = 2
            else:
                tmp["category_id"] = 1
            tmps.append(tmp)
        except:
            pass
    return tmps

def categories():
    tmps = []
    sup = ["qr", "ar"]
    cat = ["QR", "AR"]
    for i in range(2):
        tmp = cl.OrderedDict()
        tmp["supercategory"] = sup[i]
        tmp["id"] = str(i+1)
        tmp["name"] = cat[i]
        tmps.append(tmp)
    return tmps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pickle_path")
    args = parser.parse_args()
    pickle_path = args.pickle_path
    query_list = ["info","images","annotations","categories"]
    js = cl.OrderedDict()
    coord_df = pd.read_pickle(pickle_path)
    for i in range (len(query_list)):
        tmp = ""
        if query_list[i] == "info":
            tmp =info()
        elif query_list[i] == "images":
            tmp = images(coord_df)
        elif query_list[i] == "annotations":
            tmp = annotations(coord_df)
        else:
            tmp = categories()
        js[query_list[i]] = tmp
        # print("images:{}".format(js["images"][0]))
    # utils.pickle_dump(js,"../coco_pickles/{}.pickle".format(pickle_path[-21:-15]))
    fw = open("/media/akito/Data21/Experiments/201005_1107_shuffle/json_files/8hr_2class/dataset_val.json","w")
    json.dump(js,fw)

if __name__ == "__main__":
    main()