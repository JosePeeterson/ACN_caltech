import math
from numpy import datetime_as_string
import pandas as pd
import sys
import datetime
import dateutil

def base_char_cost_obj(vbat,ts_width,SOC_xtra,df,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time):
    
    begin_time = dateutil.parser.parse(begin_time)

    df = pd.read_csv('20210501-20210508 CAISO Average Price.csv')
    #print(len(df))
    # print(int(df['date'][2296][-5:-3]))
    # print(int(df['date'][2296][-2:]))
    # date = df['date'][2296][0:8]
    # print(date)
    # format_str = '%m/%d/%Y' # The format
    # datetime_obj = datetime.datetime.strptime(date, format_str)
    # print(str(datetime_obj.date()))
    price_interval = 5 # price is given for how every how many mins?
    Minute_Elec_price = {}

    i = 0
    j=0
    while(i < len(df)):
        # dt_Str = str(df['date'][i])
        # print(dt_Str)
        # in_time = datetime.datetime.strptime(dt_Str, "%m/%d/%Y %I:%M:%S %p") 
        # out_time = datetime.datetime.strftime(in_time, "%m/%d/%Y %H:%M") 
        # format_str = '%m/%d/%Y %H:%M' # The format
        # #full_date = date + " " + hr + ":" + min
        # datetime_obj = datetime.datetime.strptime(out_time, format_str) + datetime.timedelta(minutes=j)
        price = df['price ($/MWh)'][i]

        dt_Str = str(df['date'][i])
        
        format_str = '%m/%d/%Y %H:%M' # The format use %y for week2 and %Y for week1
        #full_date = date + " " + hr + ":" + min
        datetime_obj = datetime.datetime.strptime(dt_Str, format_str) + datetime.timedelta(minutes=j)
        #print(datetime_obj)
        Minute_Elec_price[datetime_obj] = ((vbat/1000) * abs(price))/1000 # Mwh -> Kwh

        j+=1
        if (j == price_interval):
            i+=1
            j=0

    WEPV = []
    viz_WEPV = {v:[] for v in range(0,Nv)}
    viz_timev_cost = {v:[] for v in range(0,Nv)}
    #print(curr_time)
    for v in range(0,Nv):
        curr_time = begin_time
        for i in range(0,TT[v]): 
            #print(curr_time)
            WEPV.append( Minute_Elec_price[curr_time] )
            viz_WEPV[v].append( Minute_Elec_price[curr_time] )
            viz_timev_cost[v].append( curr_time )
            curr_time = curr_time + datetime.timedelta(minutes=ts_width) # ts_width for timeslot width in mins


    # Charging cost Objective #1
    return WEPV,viz_WEPV, viz_timev_cost 
    


















