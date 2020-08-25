'''CNN学習用データを作成するために画像をFitsファイルから抽出するスクリプト
実行例:python3 Convert_fits_to_figure.py "/media/akito/Data1/SHARP(CEA)/2010/2010*/hmi.sharp_cea_720s.*_TAI.magnetogram.fits" "/media/akito/Data1/SHARP(CEA)/magnetgram_figs/2010"
'''
import sunpy.map
import matplotlib.pyplot as plt
import sys
import glob
from tqdm import tqdm
from joblib import Parallel,delayed
def convert_fits(path,export_dir):
    ar_num = path.split(".")[2]
    rec_time =path.split(".")[3]
    filename = "mag_figs/mag_"+str(ar_num)+"_"+str(rec_time[0:15])+".png"
    map = sunpy.map.Map(path)
    plt.figure(1)
    plt.imshow(map.data)
    plt.figure(1).savefig(filename)
    plt.axis("off")
def main():
    args =sys.argv
    source_path_str = args[1]
    source_paths = glob.glob(source_path_str)
    export_dir = args[2]
    Parallel(n_jobs=-1)([convert_fits(path,export_dir) for path in tqdm(source_paths)])
main()
