import gurobipy as gp
from gurobipy import GRB
import math
from numpy import datetime_as_string
import pandas as pd
import sys
import datetime
import dateutil

def MOO_char_cost_obj(vbat,ts_width,SOC_xtra,df,m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time):
    
    begin_time = dateutil.parser.parse(begin_time)

    df = pd.read_csv('20210522-20210531 CAISO Average Price.csv')
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
        
        format_str = '%m/%d/%y %H:%M' # The format # use %y for week2 and %Y for week1
        #full_date = date + " " + hr + ":" + min
        datetime_obj = datetime.datetime.strptime(dt_Str, format_str) + datetime.timedelta(minutes=j)
        #print(datetime_obj)
        Minute_Elec_price[datetime_obj] = ((vbat/1000) * abs(price))/1000 # Mwh -> Kwh

        j+=1
        if (j == price_interval):
            i+=1
            j=0
        

    #print(Minute_Elec_price.values())
    #sys.exit()
 
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 6)] = 27.5
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 21)] = 27.8
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 36)] = 27.3
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 51)] = 27.5
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 1, 6)] = 27.8
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 1, 21)] = 24.3
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 51)] = 27.5
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 1, 6)] = 27.8
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 1, 36)] = 24.3
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 0, 51)] = 22.5
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 1, 51)] = 23.8
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 2, 6)] = 21.3
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 2, 21)] = 23.8
    Minute_Elec_price[ datetime.datetime(2021, 5, 30, 2, 6)] = 21.3
    # Nv = 3
    # Tdep = [10,4,8]
    # del_t = 2
    t_s = 0





    # Cbat = 20
    # Ebat = 300
    # SOCdep = [0.8, 0.6, 0.7]
    # SOC_1 = [0.1, 0.2, 0.1]
    


    #print('\n',Minute_Elec_price,'\n')



    


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
            curr_time = curr_time + datetime.timedelta(minutes=ts_width)  # ts_width is timeslot width in mins








    # upper_bound battery power constraint
    bat_pwr_constr_l = []
    for v in range(0,Nv):
        for i in range(0,TT[v]): 
            bat_pwr_constr_l.append( m.addConstr( I[v][i] >= 0 ) )

    # lower_bound battery power constraint
    bat_pwr_constr_u = []
    for v in range(0,Nv):
        for i in range(0,TT[v]): 
            bat_pwr_constr_u.append( m.addConstr( I[v][i] <= Imax ) )


    # slot power constraint
    for i in range(0,max_TT):
        slot_pwr = []
        for v in range(0,Nv):
            if i < TT[v]:
                slot_pwr.append(I[v][i])
        
        m.addConstr( sum(slot_pwr) <= Icmax )

    # lower_bound Energy constraint
    #tot_char_curr = []
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
            #tot_char_curr.append(I[v][i])
        if(TT[v] > 0):
            m.addConstr( ( sum(each_veh_curr) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )

    # upper_bound Energy constraint
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
        if(TT[v] > 0):
            m.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )




    # Charging cost Objective #1
    return WEPV,viz_WEPV, viz_timev_cost 
    





