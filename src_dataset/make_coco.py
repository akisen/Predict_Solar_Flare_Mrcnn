import argparse
import collections as cl
import glob
import itertools
import json
import pathlib
from datetime import datetime as dt
import pandas as pd
import sunpy.map
from shapely.geometry import Polygon
from tqdm import tqdm
from datetime import datetime as dt
import utils

data_end = dt(2011, 8, 1)


def info():
    tmp = cl.OrderedDict()  # OrderedDict:値を追加した順序を記憶することができる辞書型風のデータ構造を提供
    tmp["descripion"] = "Predicting_Solar_Flare"
    tmp["version"] = "0.1"
    tmp["year"] = 2020
    tmp["contributor"] = "Akito Komatsu"
    tmp["data_created"] = "2020/10/01"
    return tmp


def images(paths):
    data_end = dt(2011, 8, 1)
    tmps = []
    for path in tqdm(paths, desc="image"):
        filename = path.split("/")[-1]
        datetime = filename.split(".")[2]
        datetime_dt = dt.strptime(datetime, "%Y%m%d_%H%M%S_TAI")
        if (pathlib.Path(path).exists()):
            if datetime_dt >= data_end:
                print("pass:{}".format(datetime_dt))
                pass
            else:
                # map = sunpy.map.Map(path)
                tmp = cl.OrderedDict()
                tmp["id"] = datetime[0:15]
                tmp["file_name"] = datetime[0:15] + ".jpg"
                tmp["width"] = 4102
                tmp["height"] = 4102
                tmp["date_captured"] = datetime[0:15]
                tmp["id"] = datetime[2:8] + datetime[9:11]
                tmps.append(tmp)
        # tqdm.write(str(tmp))
    return tmps


def annotations(coord_df):
    tmps = []
    coord_df = coord_df.apply(make_annotation_line, tmp=tmps, axis=1)
    # annotations = [annotation for annotation in series for series in coord_df]
    annotations = [coord_df.iloc[i][j]
                   for i in range(len(coord_df)) for j in range(len(coord_df[i]))]
    return annotations


def make_annotation_line(line, tmp):
    tmps = []

    for i in range(len(line["Polygon"])):
        tmp = cl.OrderedDict()
        polygon = Polygon(line["Polygon"][i])
        tmp["segmentation"] = [
            list(itertools.chain.from_iterable(line["Polygon"][i]))]
        tmp["area"] = polygon.area
        tmp["iscrowd"] = 0
        if (line.name >= data_end):
            print(line.name)
            exit()
        image_id = line.name.strftime("%Y%m%d%H%M%S")
        image_id = image_id[2:10]
        tmp["image_id"] = image_id
        tmp["id"] = ("{}{}".format(image_id, i + 1))
        bb_coord = polygon.bounds
        bbox = [bb_coord[0], bb_coord[1], bb_coord[2] -
                bb_coord[0], bb_coord[3] - bb_coord[1]]
        tmp["bbox"] = bbox
        # print(tmp["image_id"],tmp["id"])
        # print(line)
        if(line["C_FLARE"][i] != 0 or line["M_FLARE"][i] != 0 or line["M_FLARE"][i] != 0):
            tmp["category_id"] = 1
        else:
            tmp["category_id"] = 1
        tmps.append(tmp)
    return tmps


def categories():
    tmps = []
    # sup = ["non-flare", "flare"]
    # cat = ["non-flare", "flare"]
    # for i in range(2):
    #     tmp = cl.OrderedDict()
    #     tmp["id"] = str(i)
    #     tmp["supercategory"] = sup[i]
    #     tmp["name"] = cat[i]
    #     tmps.append(tmp)
    # return tmps
    tmp = cl.OrderedDict()
    tmp["id"] = 1
    tmp["supercategory"] = "AR"
    tmp["name"] = "AR"
    return [tmp]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="input image file path.")
    parser.add_argument("pickle_path")
    parser.add_argument("output_path")
    parser.add_argument("--mode", default="plane", help="plane or balance")
    parser.add_argument("--data", default="plane")
    args = parser.parse_args()
    image_paths = sorted(glob.glob(args.image_path))
    output_path = args.output_path
    pickle_path = args.pickle_path
    mode = args.mode
    data = args.data
    query_list = ["info", "images", "annotations", "categories"]
    js = cl.OrderedDict()
    coord_df = pd.read_pickle(pickle_path)
    if mode == "plane":
        for i in range(len(query_list)):
            tmp = ""
            if query_list[i] == "info":
                tmp = info()
            elif query_list[i] == "images":
                tmp = images(image_paths)
            elif query_list[i] == "annotations":
                tmp = annotations(coord_df)
            else:
                tmp = categories()
            js[query_list[i]] = tmp
    else:

        balance_df = pd.DataFrame(
            index=[], columns=["Polygon", "C_FLARE", "M_FLARE", "X_FLARE"])
        for series in coord_df.iterrows():
            if not (all([data == 0 for data in series[1]["C_FLARE"] + series[1]["M_FLARE"] + series[1]["X_FLARE"]])):  # フレアが発生しているかどうか判定
                series = pd.Series(series[1], index=balance_df.columns)
                balance_df = balance_df.append(series)
        if (len(image_paths) != 0):
            first_path = pathlib.Path(image_paths[0])
            image_dir = str(first_path.parent) + "/"
            dataset_name = ".".join(first_path.name.split(".")[:2])
            contents = ".".join(first_path.name.split(".")[3:])
            image_time_indexs = [dt.strptime(image_path.split(
                ".")[2], "%Y%m%d_%H%M%S_TAI") for image_path in image_paths]
            image_paths = [str(image_dir) + dataset_name + "." + index.strftime(
                "%Y%m%d_%H%M%S_TAI") + "." + contents for index in balance_df.index if index in image_time_indexs]
            # print(image_paths)
            for i in range(len(query_list)):
                tmp = ""
                if query_list[i] == "info":
                    tmp = info()
                elif query_list[i] == "images":
                    tmp = images(image_paths)
                elif query_list[i] == "annotations":
                    tmp = annotations(balance_df)
                else:
                    tmp = categories()
                js[query_list[i]] = tmp

        # print("images:{}".format(js["images"][0]))
    if(data == "merge"):
        fw = open("{}/output.json".format(output_path), "w")
        json.dump(js, fw)
    else:
        utils.pickle_dump(
            js, "{}/{}.pickle".format(output_path, pickle_path[-21:-15]))
    # fw = open("201005datasets.json","w")
    # json.dump(js,fw,indent=2)


if __name__ == "__main__":
    main()
