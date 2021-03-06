import glob
import pandas  as pd
import pickle
import utils
from tqdm import tqdm
coord_dirs = sorted(glob.glob("/home/akito/Documents/Predict_Solar_Flare_Mrcnn/coord_dfs/8hr/15months/*coord_df.pickle"))
# print(coord_dirs)
coord_df = utils.pickle_load(coord_dirs[0])
for coord_dir in tqdm(coord_dirs[1:16]):
    coord_df = pd.concat([coord_df.iloc[:-1,:],utils.pickle_load(coord_dir)])
utils.pickle_dump(coord_df,"/home/akito/Documents/Predict_Solar_Flare_Mrcnn/coord_dfs/8hr/15months/merged_df.pickle")