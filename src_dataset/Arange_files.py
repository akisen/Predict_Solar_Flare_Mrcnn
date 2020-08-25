import os
from joblib import Parallel
import glob
import sys
import shutil
def  move_figs_by_arnum(filename):
    ar_num = filename.split("_")[2]
    print(filename)
    if (os.path.exists("mag_figs_arnum/"+str(ar_num).zfill(4))):
        shutil.copyfile(filename,"mag_figs_arnum/"+str(ar_num).zfill(4)+"/"+filename.split("/")[1])
    else:
        os.mkdir("mag_figs_arnum/"+str(ar_num).zfill(4))
        shutil.copyfile(filename,"mag_figs_arnum/"+str(ar_num).zfill(4)+"/"+filename.split("/")[1])
def move_figs_by_date(filename):
    year = filename.split("_")[3][0:4]
    month =filename.split("_")[3][4:6]
    print(filename)
    if(os.path.exists("mag_figs_date/"+str(year))):
        None
    else:
        os.mkdir("mag_figs_date/"+str(year))
    if(os.path.exists("mag_figs_date/"+str(year)+"/"+str(year)+str(month).zfill(2))):
        shutil.copyfile(filename,"mag_figs_date/"+str(year)+"/"+str(year)+str(month).zfill(2)+"/"+filename.split("/")[1])
    else:
        os.mkdir("mag_figs_date/"+str(year)+"/"+str(year)+str(month).zfill(2))
        shutil.copyfile(filename,"mag_figs_date/"+str(year)+"/"+str(year)+str(month).zfill(2)+"/"+filename.split("/")[1])
def main():
    args =sys.argv
    # Parallel(n_jobs=-1)([move_figs_by_arnum(filename) for filename in sorted(glob.glob(args[1]))])
    Parallel(n_jobs=-1)([move_figs_by_date(filename) for filename in sorted(glob.glob(args[1]))])
if( __name__ == "__main__"):
    main()