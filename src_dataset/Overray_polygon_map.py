import utils
import pickle
import sys
import glob
import sunpy.map
from dateutil.relativedelta import relativedelta

args = sys.argv
full_disk_map_paths = sorted(glob.glob(args[1]))
coord_df = utils.pickle_load(args[2])
keys = ["C_FLARE","M_FLARE","X_FLARE"]
for i,full_disk_map_path in enumerate(full_disk_map_paths):
    full_disk_map = sunpy.map.Map(full_disk_map_path)
    rec_datetime = utils.str_to_datetime(full_disk_map.meta["t_rec"])
    save_path = "/media/akito/Data5/HMI_REGION/overlayed_map/{}.png".format(str(i).zfill(3))
    is_flared = [False for i in range(len(coord_df.loc[rec_datetime]["Polygon"]))]
    for i,cell in enumerate(is_flared):
        for key in keys:
            if coord_df.loc[rec_datetime][key][i]!=0:
                is_flared[i] = True

    print(rec_datetime,len(coord_df.loc[rec_datetime])) 
    utils.show_polygons_map(coord_df.loc[rec_datetime]["Polygon"],full_disk_map,save_path,is_flared)