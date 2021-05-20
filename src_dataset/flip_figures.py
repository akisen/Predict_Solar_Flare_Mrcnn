import ffmpeg
import glob
import sys
from tqdm import tqdm

input_path = sys.argv[1]
paths = sorted(glob.glob(input_path))

for path in tqdm(paths):
    output_path = path.replace("val_figs","test_figs")
    stream = ffmpeg.input(path)
    stream = ffmpeg.output(stream,output_path,vf="hflip")
    ffmpeg.run(stream)