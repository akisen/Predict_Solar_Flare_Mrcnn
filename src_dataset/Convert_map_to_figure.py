from glob import glob
import sunpy.map
import cv2
import astropy.units as u
fits_path = "/media/akito/Data/HMI_REGION/2010/*201005*/*"
paths = sorted(glob(fits_path))
# print(paths)
for i, path in enumerate(paths):
    # filename="/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/Dataset/Sun/Image/"+path.split(".")[2][0:15]+".jpg"
    filename="/home/akito/Documents/Documents/Predict_Solar_Flare_Mrcnn/Dataset/Sun/Image/forffmpeg/"+str(i).zfill(3)+".jpg"
    map=sunpy.map.Map(path)
    map_rotated = map.rotate(angle = -1*float(map.meta["crota2"])*u.deg)
    print(filename)
    cv2.imwrite(filename,map_rotated.data)