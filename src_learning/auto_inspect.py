import subprocess
import sys

for i in range(30):
    print("prediction{}".format(i+1))
    command = "python3 inspect_model.py /home/maskr-cnn/logs/{}/mask_rcnn_sun_0159.h5".format(sys.argv[1])
    subprocess.run(command,shell=True)