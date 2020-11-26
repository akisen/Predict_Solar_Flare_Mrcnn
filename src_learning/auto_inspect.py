import subprocess

for i in range(30):
    print("prediction{}".format(i+1))
    command = "python3 inspect_model.py /home/maskr-cnn/logs/sun20201119T0511/mask_rcnn_sun_0159.h5"
    subprocess.run(command,shell=True)