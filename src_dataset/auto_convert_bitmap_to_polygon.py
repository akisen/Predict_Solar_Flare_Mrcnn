import subprocess
import datetime
from dateutil.relativedelta import relativedelta

years = [2010+i for i in range(10)]
months =[i+1 for i in range(12)]
for year in years:
    for month in months:
        if(year==2010 and month<5):
            continue
        elif(year==2010 and month==5):
            command = 'python3 Convert_bitmap_polygon.py "/media/akito/Data21/hmi.Mharp_720s/{0}/{0}{1}/*.bitmap.fits"'.format(year, str(month).zfill(2))
            print(command)
            subprocess.run(command, shell=True)
        else:
            command = 'python3 Convert_bitmap_polygon.py "/media/akito/Data21/hmi.Mharp_720s/{0}/{0}{1}/*.bitmap.fits" --pickle_path "/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/Coord_series.pickle"'.format(year, str(month).zfill(2))
            print(command)
            subprocess.run(command, shell=True)
