import sys
import json
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import colorbar, xcorr
import pandas as pd
from datetime import datetime
#from new_rental_avail_obj import optimization
import gurobipy as gp
from gurobipy import GRB
import dateutil
#from char_cost_obj import cost_optimization
from New_bat_deg_obj import bat_deg_optimization
from MOO_optimization import mult_obj_opt


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


with open('ACN_DATA/acndata_1_week.json') as f:
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
    min_avail = []
    all_time_one_space_data = {}
    for i in range(0, len_events):
        if ( (data['_items'][i]['spaceID'] == j) ):
            con_time.append(data['_items'][i]['connectionTime'])
            discon_time.append(data['_items'][i]['disconnectTime'])
            if ( data['_items'][i]['userInputs'] != None):
                kw_req.append(data['_items'][i]['userInputs'][0]['kWhRequested'])
                min_avail.append(data['_items'][i]['userInputs'][0]['minutesAvailable'])
                k+=1

    all_time_one_space_data['kWhRequested'] = kw_req
    all_time_one_space_data['Connect_time'] = con_time
    all_time_one_space_data['Disconnect_time'] = discon_time
    all_time_one_space_data['Minutes_available'] = min_avail
    All_space_data[j] = all_time_one_space_data
    #print(j)

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

def convert_date_format(viz_connect_time,viz_disconnect_time,viz_opt_time,viz_I_time):

    viz_connect_time1 = {v:[] for v in range(0,len(unique_space_id))} 
    viz_disconnect_time1 = {v:[] for v in range(0,len(unique_space_id))} 
    viz_I_time1 = {v:[] for v in range(0,len(unique_space_id))} 

    for v,s in enumerate(unique_space_id):
        viz_connect_time1[v] = [dateutil.parser.parse(s) for s in viz_connect_time[v]]
        viz_disconnect_time1[v] = [dateutil.parser.parse(s) for s in viz_disconnect_time[v]]
        viz_I_time1[v] = [dateutil.parser.parse(s) for s in viz_I_time[v]]
    
    viz_opt_time1 = [dateutil.parser.parse(s) for s in viz_opt_time]

    return viz_connect_time1, viz_disconnect_time1, viz_opt_time1,viz_I_time1




del_t = 6/60 # every 6 minutes, in hours  
hr_of_day = 00
min_of_day = 00
Vbat = 410
soc_init = SOC_1 = [0]*len(unique_space_id)
Cbat = [270]*len(unique_space_id)
sch_exist = False
need_opt = False

stn_id = [""]*len(unique_space_id)
SOCdep = [0]*len(unique_space_id)
char_per = [0]*len(unique_space_id)
Nv = len(unique_space_id)

print(datetime.now())


# visualization
viz_connect_time = {v:[] for v in range(0,len(unique_space_id))} 
viz_disconnect_time = {v:[] for v in range(0,len(unique_space_id))} 
viz_opt_time = []
viz_I = {v:[] for v in range(0,len(unique_space_id))} 
viz_I_time = {v:[] for v in range(0,len(unique_space_id))} 
viz_curr_plot = {}
viz_price_plot = {}
viz_time_plot = {}
viz_WEP_plot = {}
viz_WEP_time_plot = {}
viz_TTv = []
spn = 0 # sub_plot_no 

start_date = 0
end_date = 1

for d in unique_connect_time_dates[start_date:end_date]: # index represents the date number
    print('\n')
    print(bcolors.WARNING + d + bcolors.ENDC)
    
    day_end = False

    while( not day_end):

        for v,s in enumerate(unique_space_id):
            for j in range(0,len(All_space_data[s]['Connect_time'])):
                
                if( (d ==  All_space_data[s]['Connect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Connect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Connect_time'][j][20:22])) ):
                    soc_init[v] = 0.1
                    SOC_1[v] = 0.1
                    SOCdep[v] = round((All_space_data[s]['kWhRequested'][j]*1000) / (Vbat*Cbat[v]) + soc_init[v],2)
                    char_per[v] = (All_space_data[s]['Minutes_available'][j] / 60) 
                    stn_id[v] = s
                    need_opt = True

                    date_time = d[7:11] + "-" + "05" + "-" + d[0:2] + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
                    viz_connect_time[v].append(date_time)

                    print('\n enter \n')
                    print(hr_of_day,min_of_day)
                    print(SOCdep[v])
                    print(SOCdep)
                    print(char_per[v])

                elif ( (d ==  All_space_data[s]['Disconnect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Disconnect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Disconnect_time'][j][20:22]))  ):
                    SOCdep[v] = 0
                    char_per[v] = 0
                    stn_id[v] = ""
                    SOC_1[v] = 0
                    need_opt = True

                    date_time = d[7:11] + "-" + "05" + "-" + d[0:2] + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
                    viz_disconnect_time[v].append(date_time)
                    print('\n leave \n')
                    print(hr_of_day,min_of_day)

        # print(stn_id)
        # print(SOCdep)
        # print(char_per)

        # optimisation
        if ((sum(SOCdep) > 0) and (need_opt == True) ):
            print('\n opt \n')
            print('soc1 = ', SOC_1)
            print('SOCdep = ', SOCdep)
            print('char_per = ', char_per)
            for v,s in enumerate(unique_space_id):
                if(SOC_1[v] >= SOCdep[v]):
                    SOCdep[v] = 0
                    SOC_1[v] = 0
                
                # if(char_per[v] < 0):
                #     print(char_per)
                #     print(bcolors.FAIL + "Deadline exceeded or Vehicle has not left past deadline" + bcolors.ENDC)
                #     sys.exit()
            opt_time = d[7:11] + "-" + "05" + "-" + d[0:2] + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
            viz_opt_time.append(opt_time)
            

            #TT, I_temp = optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat)
            #TT, I_temp,viz_WEPV, viz_timev = cost_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,opt_time)
            #TT, I_temp,viz_timev = bat_deg_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,opt_time)
            TT, I_temp, viz_timev_bat, viz_WEPV, viz_timev_cost = mult_obj_opt(Nv, SOCdep, char_per, SOC_1, del_t,Cbat, opt_time)

            viz_TTv.append(TT)
            for v in range(0,Nv):
                for i in range(0,TT[v]):
                    viz_curr_plot[spn,v,i] = I_temp[v,i]
                    viz_time_plot[spn,v,i] = viz_timev_bat[v][i]
                    viz_WEP_plot[spn,v,i] = viz_WEPV[v][i]
                    viz_WEP_time_plot[spn,v,i] = viz_timev_cost[v][i]
            spn+=1

            #viz_I.append(str(list(I_temp.items())))
            i=0
            cnt = 0
            sch_exist = True
            need_opt = False


        elif ((sum(SOCdep) == 0)):
            sch_exist = False
            # print('\n sum(SOCdep == 0) \n')
        # if ( (sch_exist == True)  and sum(SOCdep) == 0):
        #     for v in range(0,len(unique_space_id)):
        #         for i in TT[v]:
        #             I[v][i] = 0


       

        
        # # optimization implementation
        if ( sch_exist == True): # delta t is 6 minutes.
            if (cnt == 6):
                i+=1
                cnt=0
            cnt+=1
            for v,s in enumerate(unique_space_id):
                if( (i < TT[v]) and (TT[v] > 0) ):
                    SOC_1[v] = SOC_1[v] + ( ( (I_temp[v,i])  )*(1/60))/Cbat[v]
                    viz_I[v].append(I_temp[v,i])
                    tim = d[7:11] + "-" + "05" + "-" + d[0:2] + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00" 
                    viz_I_time[v].append(tim)

                if(char_per[v] > 0):
                    char_per[v] = char_per[v] - (1/60) # reduce 1 minute (in hours) every time    
            
        min_of_day+=1
        if (min_of_day == 60):
            hr_of_day+=1
            min_of_day = 0
        if (hr_of_day == 24):
            hr_of_day = 0
            day_end = True

        
        # Visualize charging requests and schedule

        #if (d == "01 May 2021" or "02 May 2021"):
    if spn > 10:
        break       


viz_connect_time,viz_disconnect_time,viz_opt_time,viz_I_time = convert_date_format(viz_connect_time,viz_disconnect_time,viz_opt_time,viz_I_time)



col_con = ['bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo']
col_disc = ['bx','gx','rx','cx','mx','yx','kx','wx','bx','gx','rx','cx','mx','yx']
col_I = ['b_','g_','r_','c_','m_','y_','k_','w_','b^','g^','r^','c^','m^','y^']


fig,ax2 = plt.subplots()
print("\n")
for v,s in enumerate(unique_space_id):
    print(len(viz_connect_time[v]))
    print(len(viz_disconnect_time[v]))
    for i in range(0,len(viz_disconnect_time[v])):
        ax2.plot(viz_connect_time[v][i],v,col_con[v])
        ax2.plot(viz_disconnect_time[v][i],v,col_disc[v])
        ax2.set_xlabel('Time / (date-Hr-Min)')
        ax2.set_ylabel('charging station / (#)')



for s in range(0,spn):
    fig,ax1 = plt.subplots(2)
    for v in range(0,Nv):
        for i in range(0,viz_TTv[s][v]):
            ax1[0].plot(viz_time_plot[s,v,i],viz_curr_plot[s,v,i],col_con[v])
            ax1[0].set_xlabel('Time / (date-Hr-Min)')
            ax1[0].set_ylabel('Charging current / A', color='b')
            ax1[1].plot(viz_WEP_time_plot[s,v,i],viz_WEP_plot[s,v,i],col_con[v])
            ax1[1].set_xlabel('Time / (date-Hr-Min)')
            ax1[1].set_ylabel('Charging cost / ($/Mwh)', color='b')


            # elif(s>= d and s < d + d ):
            #     ax1_2[s-d].plot(viz_time_plot[s,v,i],viz_price_plot[s,v,i],col_con[v])
            #     ax2_2[s-d] = ax1_2[s-d].twinx()      
            #     ax2_2[s-d].plot(viz_time_plot[s,v,i],viz_curr_plot[s,v,i],col_disc[v])
            # else:
            #     ax1_3[s-(d+d)].plot(viz_time_plot[s,v,i],viz_price_plot[s,v,i],col_con[v])
            #     ax2_3[s-(d+d)] = ax1_3[s-(d+d)].twinx()      
            #     ax2_3[s-(d+d)].plot(viz_time_plot[s,v,i],viz_curr_plot[s,v,i],col_disc[v])                

            # ax1[s].set_xlabel('Time / (date-Hr-Min)')
            # ax1[s].set_ylabel('Charging cost / ($/MWh)', color='b')
            # ax2.set_ylabel('Charging current / A', color='r')       
# for v,s in enumerate(unique_space_id):
#     for i in range(0,len(viz_I_time[v])):
#         #ax2.plot(viz_I_time[v][i],viz_I[v][i],col_I[v])
#         key = viz_I_time[v][i]
#         #ax1[1].plot(viz_I_time[v][i], Minute_Elec_price[viz_I_time[v][i]],'bx')


# ax1[1].set_xlabel('Time / (date-Hr-Min)')
# ax1[1].set_ylabel('Charging cost / ($/MWh)', color='b')
# ax1[0].set_xlabel('Time / (date-Hr-Min)')
# ax1[0].set_ylabel('Charging slot number / #', color='g')
# ax2.set_ylabel('Charging current / A', color='b')        
#plt.plot(viz_opt_time,viz_I)


# t = []
# p = []
# st_d = unique_connect_time_dates[start_date][0:2]
# et_d = unique_connect_time_dates[end_date][0:2]

# print(viz_disconnect_time[0][0])

# for k in Minute_Elec_price.keys():
#     if (  (int(str(k)[8:10]) >= int(st_d)) and (int(str(k)[8:10]) <=  int(et_d)) ):
        
#         t.append(k)
#         p.append(Minute_Elec_price[k])





plt.show()

print(datetime.now())




