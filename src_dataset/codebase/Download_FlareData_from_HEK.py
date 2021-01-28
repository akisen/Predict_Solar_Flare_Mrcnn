import datetime
from sunpy.net import hek
import pandas as pd
import time
from dateutil.relativedelta import relativedelta
import datetime
import calendar

def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])
client = hek.HEKClient()
years=[2014+i for i in range(6)]
s_months=[1,4,7,10]
e_months=[3,6,9,12]
print(years)
for year in years:
    for s_month,e_month in zip(s_months,e_months):
        tstart = datetime.date(year,s_month,1)
        tend = datetime.date(year,e_month,30)
        tend = get_last_date(tend)
        event_type = 'FL'
        keys =["SOL_standard","fl_goescls","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","event_starttime","event_endtime","search_observatory"]
        Flaredf =pd.DataFrame(columns=keys)
        results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
        for result in results:
            tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
            Flaredf=Flaredf.append(tmp_se,ignore_index=True)
        Flaredf=Flaredf.append(tmp_se,ignore_index=True)
        # event_type = 'CE'
        # keys =["SOL_standard","cme_accel","cme_angularwidth","cme_mass","boundbox_c1ll","boundbox_c1ur","boundbox_c2ll","boundbox_c2ur","event_starttime","event_endtime","search_observatory"]
        # results = client.search(hek.attrs.Time(tstart,tend),hek.attrs.EventType(event_type))
        # for result in results:
        #     tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
        #     Flaredf=Flaredf.append(tmp_se,ignore_index=True)
        # while (tstart< TEND):
        #     print(tstart)
        #     results = client.search(hek.attrs.Time(tstart,tstart+ relativedelta(months=1)),hek.attrs.EventType(event_type))

        #     for result in results:
        #         tmp_se=pd.Series([result[key] for key in keys],index =Flaredf.columns)
        #         Flaredf=Flaredf.append(tmp_se,ignore_index=True)
        #     tstart=tstart+ relativedelta(months=1)
        #     time.sleep(10)
        if (s_month==1):
            filename="Flare"+str(year)+"01.csv"
        elif(s_month==4):
            filename="Flare"+str(year)+"02.csv"
        elif(s_month==7):
            filename="Flare"+str(year)+"03.csv"
        elif(s_month==10):
            filename="Flare"+str(year)+"04.csv"
        print(filename)
        Flaredf.to_csv(filename)