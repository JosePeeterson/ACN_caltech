import sys
import json
import time
from matplotlib.collections import PathCollection
import matplotlib.pyplot as plt
from matplotlib.pyplot import colorbar, xcorr
import pandas as pd
# import datetime
# from datetime import datetime as dt
from datetime import datetime
#from new_rental_avail_obj import optimization
import gurobipy as gp
from gurobipy import GRB
import dateutil
#from char_cost_obj import cost_optimization
from MOO_optimization import mult_obj_opt
import numpy as np

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
        if ( (data['_items'][i]['spaceID'] == j) and ( data['_items'][i]['userInputs'] != None) ):
            con_time.append(data['_items'][i]['connectionTime'])
            discon_time.append(data['_items'][i]['disconnectTime'])
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
        fmt_str = '%d %b %Y'
        date_obj = datetime.strptime(date,fmt_str)
        if (date_obj not in unique_connect_time_dates):
            unique_connect_time_dates.append(date_obj)
    #print(All_space_data[s]['Connect_time'])
unique_connect_time_dates.sort()
    #print(All_space_data[s]['Connect_time'])

#print(unique_connect_time_dates)
#print(len(unique_space_id))

def weighted_objectives():
    weight = np.arange(0,1.1,0.5)
    W1 = []
    W2 = []
    W3 = []
    for w1 in weight:
        for w2 in weight:
            for w3 in weight:
                if w1 + w2 + w3 == 1:
                    W1.append(w1)
                    W2.append(w2)
                    W3.append(w3)

    return W1,W2,W3



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

W1,W2,W3 = weighted_objectives()

# W1 = [0]
# W2= [0]
# W3 = [1]

obj1_arr = []
obj2_arr = []
obj3_arr = []
opt_tim_arr = []
All_opt_num_v = []

for w in range(0,len(W1)):

    del_t = 6/60 # every 6 minutes, in hours  
    hr_of_day = 00
    min_of_day = 00
    Vbat = 410 #blueSG=234 prev. 410v
    soc_init = SOC_1 = [0]*len(unique_space_id) # 0 indicates No are at charging station
    Cbat = [570]*len(unique_space_id)
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
    viz_MaxTT = []
    viz_obj1 = []
    viz_obj2 = []
    viz_obj3 = []
    viz_objSUM = []
    num_v = []


    spn = 0 # sub_plot_no 
    Largest_TTv = []

    start_date = 3
    end_date = 4


    Weight = [ W1[w], W2[w], W3[w] ] 
    for d in unique_connect_time_dates[start_date:end_date]: # [start_date:end_date] index represents the date number
        date_str = d.strftime('%d') + ' ' + d.strftime('%b') + ' ' + d.strftime('%Y') 
        print('\n')
        print(bcolors.WARNING + date_str + bcolors.ENDC)
        
        day_end = False

        while( not day_end):

            for v,s in enumerate(unique_space_id):
                for j in range(0,len(All_space_data[s]['Connect_time'])):
                    
                    if( (date_str ==  All_space_data[s]['Connect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Connect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Connect_time'][j][20:22])) ):
                        soc_init[v] = 0.1
                        SOC_1[v] = 0.1
                        SOCdep[v] = round( ((All_space_data[s]['kWhRequested'][j]*1000) / (Vbat*Cbat[v]) ) + soc_init[v],2)
                        char_per[v] = (All_space_data[s]['Minutes_available'][j] / 60) 
                        stn_id[v] = s
                        need_opt = True

                        date_time = d.strftime('%Y') + "-" + "05" + "-" + d.strftime('%d') + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
                        viz_connect_time[v].append(date_time)

                        print('\n enter \n')
                        print(hr_of_day,min_of_day)
                        print('\n')
                        print(SOCdep[v])
                        print(SOCdep)
                        print(soc_init)
                        print(char_per[v])

                    elif ( (date_str ==  All_space_data[s]['Disconnect_time'][j][5:16]) and (hr_of_day == int(All_space_data[s]['Disconnect_time'][j][17:19])) and (min_of_day == int(All_space_data[s]['Disconnect_time'][j][20:22]))  ):
                        SOCdep[v] = 0
                        char_per[v] = 0
                        stn_id[v] = ""
                        SOC_1[v] = 0
                        need_opt = True

                        date_time = d.strftime('%Y') + "-" + "05" + "-" + d.strftime('%d') + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
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
                opt_time =  d.strftime('%Y') + "-" + "05" + "-" + d.strftime('%d') + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"
                #format_str = '%Y-%m-%d %H:%M:%S' # The format
                #datetime_obj = datetime.datetime.strptime(opt_time, format_str)
                viz_opt_time.append(opt_time)
                num_v.append(np.sum(np.array(SOC_1) > 0))

                #TT, I_temp = optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat)
                #TT, I_temp,viz_WEPV, viz_timev = cost_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,opt_time)
                #TT, I_temp,viz_timev = bat_deg_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,opt_time)
                TT, I_temp, viz_timev_bat, viz_WEPV, viz_timev_cost, obj1, obj2, obj3,max_TT = mult_obj_opt(Weight,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, opt_time,Vbat)
                viz_MaxTT.append(max_TT)
                Largest_TTv.append(sum(TT))
                viz_TTv.append(TT)
                viz_obj1.append(obj1)
                viz_obj2.append(obj2)
                viz_obj3.append(obj3)
                viz_objSUM.append(obj1 + obj2 + obj3)
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
                #break

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
                        tim =  d.strftime('%Y') + "-" + "05" + "-" +  d.strftime('%d') + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00" 
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
        # if spn > 10:
        #     break

    obj1_arr.append(viz_obj1)
    obj2_arr.append(viz_obj2)
    obj3_arr.append(viz_obj3)
    All_opt_num_v.append(num_v)

    print("largest TTv = ", max(Largest_TTv) )

    viz_connect_time,viz_disconnect_time,viz_opt_time,viz_I_time = convert_date_format(viz_connect_time,viz_disconnect_time,viz_opt_time,viz_I_time)
    opt_tim_arr.append(viz_opt_time)

    #col_con1 = ['bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo','ko','wo']
    #col_con = ['b-','g-','r-','c-','m-','y-','k-','w-','b-','g-','r-','c-','m-','y-','k-','w-','b-','g-','r-','c-','m-','y-','k-','w-']
    #col_disc = ['bx','gx','rx','cx','mx','yx','kx','wx','bx','gx','rx','cx','mx','yx','bx','gx','rx','cx','mx','yx','kx','wx']
    #col_I = ['b_','g_','r_','c_','m_','y_','k_','w_','b^','g^','r^','c^','m^','y^']
    #col_stack = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w','b', 'g', 'r', 'c', 'm', 'y', 'k', 'w','b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    col_con1 = plt.cm.nipy_spectral(np.linspace(0,1,30))
    col_con = plt.cm.nipy_spectral(np.linspace(0,1,30))
    col_disc = plt.cm.nipy_spectral(np.linspace(0,1,30))
    col_stack = plt.cm.nipy_spectral(np.linspace(0,1,30))
    ################ VISUALIZE Individual plots of objective values vs opt. time at each of the weight combinations ################
    # print(viz_opt_time,len(viz_obj1))
    # plt.figure()
    # plt.title('Objective function value    Vs.   optimization time')
    # plt.plot(viz_opt_time,viz_obj1,'ro-',label='Charging cost')
    # plt.plot(viz_opt_time,viz_obj2,'go-',label='Bat. Deg. cost')
    # plt.plot(viz_opt_time,viz_obj3,'bo-',label='availability cost')
    # plt.text(viz_opt_time[0],0.001,'CC_W1 = '+ str( len(viz_opt_time)) + ' ' + str( len(viz_obj1)) )
    # plt.text(viz_opt_time[0],0.002,'CC_W1 = '+ str( len(viz_opt_time)) + ' ' + str( len(viz_obj2)) )
    # plt.text(viz_opt_time[0],-0.001,'CC_W1 = '+ str( len(viz_opt_time)) + ' ' + str( len(viz_obj3)) )

    #plt.text(viz_opt_time[0],0.002,'BD_W2 = '+str(W2[w]))
    #plt.text(viz_opt_time[0],-0.001,'AV_W3 = '+str(W3[w]))
    #plt.plot(viz_opt_time,viz_objSUM,'m-',label='Total cost')
    #plt.legend()
    ################    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################

    # ################## VISUALIZE Stack plots of objective values vs opt. time at each of the weight combinations ################
    # print('\n')
    # stack = [viz_obj1,viz_obj2,viz_obj3]
    # y = np.vstack(stack)
    # fig, ax4 = plt.subplots()
    # ax4.stackplot(viz_opt_time, y)
    # ################    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################


    # ################# VISUALIZE Current for each vehicle Vs. opti. time ################
    # for s in range(0,spn):
    #     fig,ax1 = plt.subplots(2)
    #     viz_tot_curr = np.array([0]*viz_MaxTT[s])
    #     viz_stack_y = []
    #     curr_stack ={v:[] for v in range(0,Nv)}

    #     for v in range(0,Nv):
    #         x = []
    #         y = []
    #         x1 = []
    #         y1 = []

    #         for i in range(0,viz_TTv[s][v]):
    #             x.append(viz_time_plot[s,v,i])
    #             y.append(viz_curr_plot[s,v,i])
    #             x1.append(viz_WEP_time_plot[s,v,i])
    #             y1.append(viz_WEP_plot[s,v,i])

    #         y_temp = np.pad(y,(0,viz_MaxTT[s] - viz_TTv[s][v]),mode='constant')
    #         x_temp = np.pad(x,(0,viz_MaxTT[s] - viz_TTv[s][v]),mode='constant')

    #         viz_tot_curr = viz_tot_curr + y_temp
    #         if viz_TTv[s][v] == viz_MaxTT[s]:
    #             viz_x_tot_cur =x
                
    #         viz_stack_y.append(y_temp)
    #         curr_stack[v] = y_temp

    #         ax1[0].plot(x,y,color=col_con[v], label=col_con[v])
    #         ax1[0].set_xlabel('Time / (date-Hr-Min)')
    #         ax1[0].set_ylabel('Charging current / A', color='b')

    #         ax1[1].plot(x1,y1,color=col_con[v])
    #         ax1[1].set_xlabel('Time / (date-Hr-Min)')
    #         ax1[1].set_ylabel('Charging cost / ($/Mwh)', color='b')

    #     ax1[0].plot(viz_x_tot_cur,viz_tot_curr,color=col_con[v+1])
    #     ax1[0].legend()
    #     # plt.figure()
    #     # plt.plot(viz_x_tot_cur,viz_tot_curr,'k-')

    #     ## Bar STACKPLOT
    #     df = pd.DataFrame(curr_stack, index=viz_x_tot_cur)
    #     if not df.empty:
    #         ax = df.plot.bar(stacked=True,color=col_stack, )

    #    # # continuous STACKPLOT
    #    # print('\n')
    #    # print(len(viz_stack_y))
    #    # y = np.vstack(viz_stack_y)
    #    # fig, ax = plt.subplots()
    #    # ax.stackplot(viz_x_tot_cur, y)
    # ###############    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################



################## VISUALIZE Overall plots of objective values vs opt. time at each of the weight combinations ################
plt.figure()
plt.title('Objective function value    Vs.   optimization time for different weights')
opt_num = 9
opt_time_instance = opt_tim_arr[0][opt_num]
obj1_space = []
l=len(obj1_arr)
colors= plt.cm.Greens(np.linspace(0,1,l+2))
for i in range(0,l):
    plt.plot(opt_tim_arr[i],obj1_arr[i] ,color=colors[i+2],marker='o')
    obj1_space.append(obj1_arr[i][opt_num])

obj2_space = []
l=len(obj2_arr)
colors= plt.cm.Blues(np.linspace(0,1,l+2))
for i in range(0,l):
    plt.plot(opt_tim_arr[i],obj2_arr[i] ,color=colors[i+2],marker='o')
    obj2_space.append(obj2_arr[i][opt_num])

obj3_space = []
l=len(obj3_arr)
colors= plt.cm.Oranges(np.linspace(0,1,l+2))
for i in range(0,l):
    plt.plot(opt_tim_arr[i],obj3_arr[i] ,color=colors[i+2],marker='o')
    obj3_space.append(obj3_arr[i][opt_num])

plt.text(viz_opt_time[0],0.002,'CC_obj1 = Light green to dark')
plt.text(viz_opt_time[0],0.001,'BD_obj2 = Light blue to dark')
plt.text(viz_opt_time[0],-0.001,'AV_obj3 = Light orange to dark')
plt.text(viz_opt_time[0],0.0075,'W1 = '+str(W1))
plt.text(viz_opt_time[0],0.0065,'W2 = '+str(W2))
plt.text(viz_opt_time[0],0.0055,'W3 = '+str(W3))
#plt.plot(viz_opt_time,viz_objSUM,'m-',label='Total cost')
################    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################






################## VISUALIZE Connect and disconnect times ################
fig,ax2 = plt.subplots()
print("\n")
for v,s in enumerate(unique_space_id):
    print(len(viz_connect_time[v]))
    print(len(viz_disconnect_time[v]))
    #stop = min([len(viz_disconnect_time[v]),len(viz_connect_time[v])])
    for l in viz_connect_time[v]:
        ax2.plot(l,v,color=col_con1[v],marker='o')

    for k in viz_disconnect_time[v]:
        ax2.plot(k,v,color=col_disc[v],marker='x')
ax2.set_xlabel('Time / (date-Hr-Min)')
ax2.set_ylabel('charging station / (#)')
################    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################


print(max(All_opt_num_v))

# ################## VISUALIZE objective values Space curve for different weights: ################
ax = plt.figure().add_subplot(projection='3d')
x = obj1_space
y = obj2_space
z = obj3_space
#colors= plt.cm.rainbow(np.linspace(1,1,6))
ax.plot(x, y, z,c='g',markevery=[0],marker='o')
ax.plot(x, y, z, label='opt. time = ' + str(opt_time_instance),c='g',marker='x')
ax.set_xlabel('Charging cost obj')
ax.set_ylabel('Battery deg. obj')
ax.set_zlabel('Availability obj ')
ax.set_title('W1 = '+str(W1) + ', ' + 'W2 = '+str(W2) + ', ' +  'W3 = '+str(W3) )
ax.legend()
# ################    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    ####################

plt.show()


'''

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
'''



