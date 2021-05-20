import ast
import glob
import os
import sys
import time
from datetime import datetime as dt

import pandas as pd
from tqdm import tqdm


def preprocess_df(flare_df):
    for _ in range(5):
        if flare_df.iloc[0].name.minute == 0:
            return flare_df
        else:
            flare_df = flare_df.drop(flare_df.index[0])


def calculate_largest_flare_1hour(flare_df):
    flare_ranks = ["B", "C", "M", "X"]
    for i in range(len(flare_df)-5):
        f_class = 0
        if (time := flare_df.iloc[i].name).minute == 0:
            for j in range(5):
                for flare_rank in flare_ranks:
                    try:
                        if(flare_label := flare_df.iloc[i+j]["{}FLARE_LABEL_LOC".format(flare_rank)]) != "None":
                            try:
                                if(f_class < (tmp := float(ast.literal_eval(flare_label)["magnitude"][1:]))):
                                    f_class = tmp
                                    flare_df.at[time,
                                                "{}FLARE_LABEL_LOC".format(flare_rank)] = flare_label
                                    tqdm.write("time:{},data:{},rank:{}".format(
                                        flare_df.iloc[i].name, flare_df.at[time, "{}FLARE_LABEL_LOC".format(flare_rank)], flare_rank))
                            except ValueError:
                                pass
                            except SyntaxError:
                                print("error:{},{}".format(time, flare_label))
                    except IndexError:
                        pass
    return flare_df.asfreq("1H")


def main():
    input_paths = sorted(glob.glob(sys.argv[1]))
    filedir = sys.argv[2]
    for input_path in tqdm(input_paths):
        filename = os.path.basename(input_path)
        tqdm.write(filename)
        output_path = sys.argv[2]+"/"+filename
        swan_df = pd.read_table(input_path, index_col=0, parse_dates=True)
        swan_df = preprocess_df(swan_df)
        calculate_largest_flare_1hour(swan_df).to_csv(output_path)


main()
