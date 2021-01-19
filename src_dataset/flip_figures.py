import subprocess
import sys
import glob
paths = glob.glob(sys.argv[1])

for path in paths:
    output_path = path.replace("val_figs","fliped_val_figs")
    command = "ffmpeg -i {} -vf hflip {}".format(path,output_path)
    subprocess.run(command, shell=True)
