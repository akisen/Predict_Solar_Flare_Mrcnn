import utils
import pickle
import sys
import glob
import sunpy.map

args = sys.argv
full_disk_map_paths = sorted(glob.glob(args[1]))
coord_series = utils.pickle_load(args[2])
for full_disk_map_path in full_disk_map_paths:
    full_disk_map = sunpy.map.Map(full_disk_map_path)
    # print( {key:value for key,value  in full_disk_map.meta.items()})
    rec_datetime = utils.str_to_datetime(full_disk_map.meta["t_rec"])
    save_path = "/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/samples/sun/Overrayed_map_cleared0927/"+str(rec_datetime)+".png"
    print(rec_datetime,len(coord_series[rec_datetime]))
    utils.show_polygons_map(coord_series[rec_datetime],full_disk_map,save_path)