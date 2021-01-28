import sys
import glob
import utils 
from datetime import datetime as dt
import cv2
import numpy as np
from shapely.geometry import Polygon
from tqdm import tqdm
args = sys.argv
fig_paths = sorted(glob.glob(args[1]))
coord_df = utils.pickle_load(args[2])
alpha = 0.5
int_coords = lambda x:np.array(x).round().astype(np.int32)

for fig_path in tqdm(fig_paths):
    obs_time = dt.strptime(fig_path[-19:-4],"%Y%m%d_%H%M%S")
    image = cv2.imread(fig_path)
    overlay = image.copy()
    for p in coord_df.loc[obs_time]["Polygon"]:
        polygon =Polygon(p)
        exterior = [int_coords(polygon.exterior.coords)]
        cv2.polylines(overlay,exterior,color=(255,255,0),isClosed=True,thickness = 10)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    filename =fig_path.replace("train_figures", "overlayed_figures")
    cv2.imwrite(filename, image)

