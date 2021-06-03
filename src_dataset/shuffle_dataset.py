import utils
import glob
import pandas as pd
import sys
output_dir = sys.argv[1]
coord_df_paths = glob.glob("/media/akito/Data21/Experiments/resample(202105)/balance_dataset/201005_1107_shuffle/coord_df/*.pickle")
coord_df = utils.pickle_load(coord_df_paths[0])
# print(coord_df)
for coord_df_path in coord_df_paths:
    coord_df = pd.concat([coord_df, utils.pickle_load(coord_df_path)])
shuffled_df = coord_df.sample(frac=1)
split_num = int(len(shuffled_df)*0.8)
train_df = shuffled_df.iloc[:split_num,:]
val_df = shuffled_df.iloc[split_num:,:]
train_df.to_pickle("{}/train_df.pickle".format(output_dir))
val_df.to_pickle("{}/val_df.pickle")