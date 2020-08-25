import subprocess

years=[ 2010+i for i in range(4)]
months = [i+1 for i in range(12)]
days = [i+1 for i in range(31)]
for year in years:
    for month in months:
        for day in days:
            command ='python3 Convert_fits_to_figure.py "/media/akito/Data1/SHARP(CEA)/'+str(year)+'/'+str(year)+str(month).zfill(2)+'/*'+str(year)+str(month).zfill(2)+str(day).zfill(2)+'*.magnetogram.fits"'+' "/media/akito/Data1/SHARP(CEA)/magnetgram_figs/'+str(year)+'"'
            if (month<=4 and year==2010):
                continue
            else:
                print(command)
                subprocess.run(command,shell=True)