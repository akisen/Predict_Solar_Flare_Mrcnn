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

def info():
    tmp = cl.OrderedDict() # OrderedDict:値を追加した順序を記憶することができる辞書型風のデータ構造を提供
    tmp["descripion"] = "Predicting_Solar_Flare"
    tmp["version"] = "0.1"
    tmp["year"] = 2020
    tmp["contributor"] = "Akito Komatsu"
    tmp["data_created"] = "2020/10/01"
    return tmp

def images(paths):
    print("images:{}".format(paths))
    tmps =[]
    for path in tqdm(paths,desc="image"):
        tmp = cl.OrderedDict()
        map = sunpy.map.Map(path)
        filename =path.split("/")[-1]
        datetime = filename.split(".")[2]
        tmp["id"] = datetime[0:15]
        tmp ["file_name"] = datetime[0:15]+".png"
        tmp["width"] = 4102
        tmp["height"] = 4102
        tmp["date_captured"] = map.meta['t_rec'][:-4]
        tmp["id"] = datetime[2:8]+datetime[9:11]
        tmps.append(tmp)
        # tqdm.write(str(tmp))
    return tmps

def annotations(coord_df):
    tmps = []
    coord_df = coord_df.apply(make_annotation_line,tmp=tmps,axis=1)
    # annotations = [annotation for annotation in series for series in coord_df]
    annotations = [coord_df.iloc[i][j] for i in range(len(coord_df)) for j in range(len(coord_df[i]) )]
    print(len(annotations))
    return annotations

def make_annotation_line(line,tmp):
    tmps = []
    for i in tqdm(range(len(line["Polygon"])),desc="Annotation"):
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
        # print(tmp["image_id"],tmp["id"])
        # print(line)
        if(line["C_FLARE"][i]!=0 or line["M_FLARE"][i]!=0 or line["M_FLARE"][i]!=0 ):
            tmp["category_id"] = 1
        else:
            tmp["category_id"] = 0
        tmps.append(tmp)
    return tmps

def categories():
    tmps = []
    sup = ["qr", "ar"]
    cat = ["QR", "AR"]
    for i in range(2):
        tmp = cl.OrderedDict()
        tmp["id"] = str(i)
        tmp["supercategory"] = sup[i]
        tmp["name"] = cat[i]
        tmps.append(tmp)
    return tmps

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path",help="input image file path.")
    parser.add_argument("pickle_path")
    parser.add_argument("--mode",default="plane",help="plane or balance")
    args = parser.parse_args()
    image_paths = args.image_path
    pickle_path = args.pickle_path
    mode = args.mode
    query_list = ["info","images","annotations","categories"]
    js = cl.OrderedDict()
    coord_df = pd.read_pickle(pickle_path)
    if mode =="plane":
        for i in range (len(query_list)):
            tmp = ""
            if query_list[i] == "info":
                tmp =info()
            elif query_list[i] == "images":
                tmp = images(glob.glob(image_paths))
            elif query_list[i] == "annotations":
                tmp = annotations(coord_df)
            else:
                tmp = categories()
            js[query_list[i]] = tmp
    else:
        balance_df = pd.DataFrame(index=[],columns =["Polygon","C_FLARE","M_FLARE","X_FLARE"])
        for series in coord_df.iterrows():
            if (all ([data == 0 for data in series[1]["C_FLARE"]+series[1]["M_FLARE"]+series[1]["X_FLARE"]])): # フレアが発生しているかどうか判定
                pass
            else:
                series = pd.Series(series[1],index=balance_df.columns)
                balance_df = balance_df.append(series)
        # TODO:Pathlibで再実装
        image_dir = ".".join(glob.glob(image_paths)[0].split(".")[:-4])
        image_paths = [image_dir+"."+index.strftime("%Y%m%d_%H%M%S_TAI")+"."+".".join(glob.glob(image_paths)[0].split(".")[-3:]) for index in balance_df.index]
        print(image_paths[0])
        for i in range (len(query_list)):
            tmp = ""
            if query_list[i] == "info":
                tmp =info()
            elif query_list[i] == "images":
                tmp = images(image_paths)
            elif query_list[i] == "annotations":
                tmp = annotations(balance_df)
            else:
                tmp = categories()
            js[query_list[i]] = tmp

        # print("images:{}".format(js["images"][0]))
    utils.pickle_dump(js,"../out/coco_pickles/{}.pickle".format(pickle_path[-21:-15]))
    # fw = open("201005datasets.json","w")
    # json.dump(js,fw,indent=2)

if __name__ == "__main__":
    main()