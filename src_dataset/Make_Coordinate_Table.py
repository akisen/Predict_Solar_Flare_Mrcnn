# 太陽の全球MapやMaskmapを回転させる際に参考にするCSVファイルを作成するスクリプト
import pandas as pd
import datetime
import glob
import sunpy.map
years=[i+2011 for i in range(5)]
columns = ["time","referencex","referencey","chaincode"]
coordinate_df = pd.DataFrame(columns=columns)
for year in years:
    START_TIME = datetime.datetime(year,1,1,0,0,0)
    END_TIME = datetime.datetime(year+1,1,1,0,0,0)
    time =START_TIME
    while time != END_TIME:
        print(time)
        line = pd.Series([time,0,0,0],index=coordinate_df.columns)
        coordinate_df = coordinate_df.append(line,ignore_index =True)
        time= time+datetime.timedelta(hours=1)
    hmi_region_path = "/media/akito/Data/HMI_REGION/"+str(year)+"/*.fits"
    hmi_region_files= sorted(glob.glob(hmi_region_path))
    hmi_region_files[0]
    for hmi_region_file in hmi_region_files:
        print(hmi_region_file)
        hmi_region_map = sunpy.map.Map(hmi_region_file)
        t_rec = datetime.datetime.strptime(hmi_region_map.meta["t_rec"],"%Y.%m.%d_%H:%M:%S_TAI")
        coordinate_df.loc[coordinate_df["time"]==t_rec,"referencex"]= hmi_region_map.reference_pixel[0].value
        coordinate_df.loc[coordinate_df["time"]==t_rec,"referencey"]= hmi_region_map.reference_pixel[1].value
    coordinate_df.to_csv(str(year)+".csv")