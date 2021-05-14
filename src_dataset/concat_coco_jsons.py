import pickle
import json
import pandas as pd
import argparse
import utils
import glob
import collections as cl
from make_coco import info
from make_coco import categories
from tqdm import tqdm
parser = argparse.ArgumentParser()

parser.add_argument('input_path' )
parser.add_argument('output_path')

args = parser.parse_args()
input_paths = glob.glob(args.input_path)
output_path = args.output_path

def main ():
    js = cl.OrderedDict()
    js["info"] = info()
    js["images"] = []
    js["annotations"] = []
    js["categories"] = categories()
    file_count = 0
    anno_count = 0
    for input_path in tqdm(input_paths):
        tmp = utils.pickle_load(input_path)
        js["images"].extend(tmp["images"])
        file_count+=len((tmp["images"]))
        js["annotations"].extend(tmp["annotations"])
        anno_count += len(tmp["annotations"])
    with open( output_path , "w") as f:
        json.dump(js,f)
    print("files"+str(file_count))
    print("annotations"+str(anno_count))
main()