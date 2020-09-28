import json
import collections as cl
import argparse
import sunpy.map
import glob
import pickle
import pandas as pd
def info():
    tmp = cl.OrderedDict() # OrderedDict:値を追加した順序を記憶することができる辞書型風のデータ構造を提供
    tmp["descripion"] = "Predicting_Solar_Flare"
    tmp["version"] = "0.1"
    tmp["year"] = 2020
    tmp["contributor"] = "Akito Komatsu"
    tmp["data_created"] = "2020/10/01"
    return tmp

def images(paths):
    paths = glob.glob(paths)
    tmps =[]
    for path in paths:
        tmp = cl.OrderedDict()
        map = sunpy.map.Map(path)
        filename =path.split("/")[-1]
        datetime = filename.split(".")[2]
        tmp["id"] = datetime[0:15]
        tmp ["file_name"] = datetime[0:15]+".png"
        tmp["width"] = 4096
        tmp["height"] =4096
        tmp["date_captured"] = map.meta['t_rec'][:-4]
        tmps.append(tmp)
    return tmps
def annotations(pickle_path):
    tmps = []
    print(pickle_path)
    coord_df = pd.read_pickle(pickle_path)
    print(coord_df.keys())
    #TODO: CoordSeriesを拡張して横に一列追加→フレアラベルのリストを追記
    exit()
    return tmps
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path",help="input file path.")
    parser.add_argument("pickle_path")
    args = parser.parse_args()
    paths = args.path
    pickle_path = args.pickle_path
    query_list = ["info","images","annotations"]
    js = cl.OrderedDict()
    for i in range (len(query_list)):
        tmp = ""
        if query_list[i] == "info":
            tmp =info()
        elif query_list[i] == "images":
            tmp = images(paths)
        else:
            tmp = annotations(pickle_path)
        js[query_list[i]] = tmp
    fw = open("datasets.json","w")
    json.dump(js,fw,indent=2)

if __name__ == "__main__":
    main()