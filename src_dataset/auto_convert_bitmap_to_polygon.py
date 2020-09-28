import subprocess
import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
years = [2010+i for i in range(10)]
months =[i+1 for i in range(12)]
with tqdm(total = len(years) * len(months)-4) as pbar:
    for year in years:
        for month in months:
            if(year==2010 and month<5):
                continue
            elif(year==2010 and month==5):
                command = 'python3 Convert_bitmap_polygon.py "/media/akito/Data21/hmi.Mharp_720s/{0}/{0}{1}/*.bitmap.fits" "/media/akito/Data/SWAN_Flare/dataverse_files/SWAN/*/*"'.format(year, str(month).zfill(2))
                print(command)
                pbar.update(1)
                subprocess.run(command, shell=True)
            else:
                command = 'python3 Convert_bitmap_polygon.py "/media/akito/Data21/hmi.Mharp_720s/{0}/{0}{1}/*.bitmap.fits" "/media/akito/Data/SWAN_Flare/dataverse_files/SWAN/*/*" --pickle_path "/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/Coord_series.pickle"'.format(year, str(month).zfill(2))
                print(command)
                pbar.update(1)
                subprocess.run(command, shell=True)
