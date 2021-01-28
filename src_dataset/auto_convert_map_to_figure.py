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
            else:
                command = 'python3 Convert_map_to_figure.py "/media/akito/Data21/HMI.ME_720s_fd10/{0}/{0}{1}/" "/media/akito/Data21/HMI.ME_720s_fd10/figures/" --channel 3'.format(year, str(month).zfill(2))
                print(command)
                pbar.update(1)
                subprocess.run(command, shell=True)
            