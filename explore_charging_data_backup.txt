import sys
import json
import time
import pandas as pd
from datetime import datetime
from new_rental_avail_obj import optimization
import gurobipy as gp
from gurobipy import GRB

with open('acndata_1_week.json') as f:
    data = json.load(f)

len_events = len(data['_items'])

unique_space_id = []

for i in range(0, len_events):
    if ( data['_items'][i]['spaceID'] not in unique_space_id):
        unique_space_id.append(data['_items'][i]['spaceID'])

All_space_data = {}
k=0
for j in unique_space_id:
    con_time = []
    discon_time = []
    kw_req = []
    kw_del = []
    all_time_one_space_data = {}
    for i in range(0, len_events):
        if ( (data['_items'][i]['spaceID'] == j) ):
            con_time.append(data['_items'][i]['connectionTime'])
            discon_time.append(data['_items'][i]['disconnectTime'])
            if ( data['_items'][i]['userInputs'] != None):
                kw_req.append(data['_items'][i]['userInputs'][0]['kWhRequested'])
                kw_del.append(data['_items'][i]['userInputs'][0]['minutesAvailable'])
                k+=1

    all_time_one_space_data['kWhRequested'] = kw_req
    all_time_one_space_data['Connect_time'] = con_time
    all_time_one_space_data['Disconnect_time'] = discon_time
    all_time_one_space_data['Minutes_available'] = kw_del
    All_space_data[j] = all_time_one_space_data
    #print(j)

each_veh_connect_times = []
unique_connect_time_dates = []

for s in unique_space_id:
    # print(s)
    # print(len(All_space_data[s]['kWhRequested']))
    # print(len(All_space_data[s]['Minutes_available']))
    # print(len(All_space_data[s]['Disconnect_time']))
    # print(len(All_space_data[s]['Connect_time']))
    # print('\n')
    for d in All_space_data[s]['Connect_time']:
        date = d[5:16]
        if (date not in unique_connect_time_dates):
            unique_connect_time_dates.append(date)
    #print(All_space_data[s]['Connect_time'])

#print(unique_connect_time_dates)
#print(len(unique_space_id))



del_t = 6/60 # every 6 minutes, in hours  
hr_of_day = 00
min_of_day = 00
day_end = False
Vbat = 410
soc_init = SOC_1 = [0]*len(unique_space_id)
Cbat = [270]*len(unique_space_id)
sch_exist = False

stn_id = [""]*len(unique_space_id)
SOCdep = [0]*len(unique_space_id)
char_per = [0]*len(unique_space_id)


print(datetime.now())

for d in unique_connect_time_dates[0:1]: # index represents the date number
    print(d)
    


    while( not day_end):

        for v,s in enumerate(unique_space_id):
            for j in range(0,len(All_space_data[s]['Connect_time'])):
                
                if( (d ==  All_space_data[s]['Connect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Connect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Connect_time'][j][20:22])) ):
                    soc_init[v] = 0.1
                    SOC_1[v] = 0.1
                    SOCdep[v] = (All_space_data[s]['kWhRequested'][j]*1000) / (Vbat*Cbat[v]) + soc_init[v]
                    char_per[v] = (All_space_data[s]['Minutes_available'][j] / 60) 
                    stn_id[v] = s
                    need_opt = True
                    print('\n enter \n')
                    print(hr_of_day,min_of_day)
                elif ( (d ==  All_space_data[s]['Connect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Disconnect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Disconnect_time'][j][20:22]))  ):
                    SOCdep[v] = 0
                    char_per[v] = 0
                    stn_id[v] = ""
                    SOC_1[v] = 0
                    need_opt = True
                    print('\n leave \n')
                    print(hr_of_day,min_of_day)

        # print(stn_id)
        # print(SOCdep)
        # print(char_per)

        # optimisation
        if ((sum(SOCdep) > 0) and (need_opt == True) ):
            print('\n opt \n')
            I, TT, m,I_temp = optimization(len(unique_space_id), SOCdep, char_per, SOC_1, del_t,Cbat)
            #print(I)
            i=0
            cnt = 0
            sch_exist = True
            need_opt = False

        elif ((sum(SOCdep) == 0)):
            sch_exist = False
        # if ( (sch_exist == True)  and sum(SOCdep) == 0):
        #     for v in range(0,len(unique_space_id)):
        #         for i in TT[v]:
        #             I[v][i] = 0


       

        
        # # optimization implementation
        if ( sch_exist == True): # delta t is 6 minutes.
            if (cnt == 6):
                i+=1
            cnt+=1
            for v,s in enumerate(unique_space_id):
                if(i < TT[v] and TT[v] > 0):
                    SOC_1[v] = SOC_1[v] + ( ( (I_temp[v,i])  )*(1/60))/Cbat[v]

        min_of_day+=1
        if (min_of_day == 60):
            hr_of_day+=1
            min_of_day = 0
        if (hr_of_day == 24):
            hr_of_day = 0
            day_end = True

        
        # print(stn_id)
        # print(SOCdep)
        # print(char_per)

print(datetime.now())




