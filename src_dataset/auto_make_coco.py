import subprocess
from tqdm import tqdm
years = [2010 + i for i in range(10)]
months = [i + 1 for i in range(12)]
with tqdm(total=len(years) * len(months) - 4) as pbar:
    for year in years:
        for month in months:
            if(year == 2010 and month < 5):
                continue
            else:
                command = 'python3 make_coco.py "/media/akito/Data5/HMI_REGION/{0}/{0}{1}/*fits" "/media/akito/Data21/Experiments/coord_dfs/24hr/{0}{1}coord_df.pickle" "/media/akito/Data21/Experiments/unbalance_dataset/201005-201912/coco_pickles"  --mode plane'.format(
                    year, str(month).zfill(2))
                tqdm.write(command)
                pbar.update(1)
                subprocess.run(command, shell=True)
