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
    js["images"] = []
    js["annotations"] = []
    js["info"] = info()
    js["categories"] = categories()
    for input_path in tqdm(input_paths):
        tmp = utils.pickle_load(input_path)
        js["images"].extend(tmp["images"])
        js["annotations"].extend(tmp["annotations"])
    with open(output_path,"w") as f:
        json.dump(js,f,indent=2)

main()