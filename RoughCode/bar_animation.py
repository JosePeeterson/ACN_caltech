import math as m
from time import strptime
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from datetime import datetime
from datetime import datetime, timedelta 
import sys
import matplotlib.pyplot as plt
import pandas as pd

def create_electricity_price():

    df = pd.read_csv('20210501-20210508 CAISO Average Price.csv')

    price_interval = 5 # price is given for how every how many mins?
    Minute_Elec_price = {}
    i = 420
    j=0
    while(i < 708):
        price = df['price ($/MWh)'][i]
        dt_Str = str(df['date'][i])
        format_str = '%m/%d/%Y %H:%M' # The format
        #full_date = date + " " + hr + ":" + min
        datetime_obj = datetime.strptime(dt_Str, format_str) + timedelta(minutes=j)
        #print(datetime_obj)
        Minute_Elec_price[datetime_obj] = abs(price)/1000 # Mwh -> Kwh
        j+=1
        if (j == price_interval):
            i+=1
            j=0

    return Minute_Elec_price


def create_demand_impulse():

    # flat_res = np.zeros(5*12*7)

    flat_imp = 100*signal.unit_impulse(5*12*7, 'mid')
    b, a = signal.butter(2, 0.01)
    flat_res = signal.lfilter(b, a, flat_imp)
    res_idx = np.where(flat_res < 0)
    flat_res[res_idx] = -1*flat_res[res_idx]


    morn_imp = 600*signal.unit_impulse(2*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    morn_response = signal.lfilter(b, a, morn_imp)
    res_idx = np.where(morn_response < 0)
    morn_response[res_idx] = -1*morn_response[res_idx]

    flat_res1 = np.zeros(5*12*3)

    noon_imp = 600*signal.unit_impulse(2*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    noon_response = signal.lfilter(b, a, noon_imp)
    res_idx = np.where(noon_response < 0)
    noon_response[res_idx] = -1*noon_response[res_idx]

    flat_res2 = np.zeros(5*12*3)

    eve_imp = 600*signal.unit_impulse(3*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    eve_response = signal.lfilter(b, a, eve_imp)
    res_idx = np.where(eve_response < 0)
    eve_response[res_idx] = -1*eve_response[res_idx]

    eve_imp = 250*signal.unit_impulse(12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    eve_response1 = signal.lfilter(b, a, eve_imp)
    res_idx1 = np.where(eve_response1 < 0)
    eve_response1[res_idx1] = -1*eve_response1[res_idx1]

    flat_res3 = np.zeros(5*12*3)

    demand = np.concatenate((flat_res, morn_response, flat_res1, noon_response, \
        flat_res2,  eve_response, eve_response1, flat_res3))

    return demand

def battery_degradation_cost():

    flat_1 = np.zeros(5*12*2)

    x = np.arange(0,5*12*1,1)
    line1 = 0.0005*x

    flat_2 = np.zeros(5*12*2)

    y = np.arange(0,5*12*3,1)
    line2 = 0.0009*y

    flat_3 = np.zeros(5*12*3)

    z = np.arange(0,5*12*2,1)
    line3 = 0.001*z

    flat_4 = np.zeros(5*12*3)

    a = np.arange(0,5*12*2,1)
    line4 = 0.002*a

    flat_5 = np.zeros(5*12*2)

    a = np.ones(int(5*12*0.5))
    a1 = np.arange(0,5*12*0.5,1)
    line5 = 0.05*a + 0.0005*a1

    flat_6a = np.zeros(int(5*12*0.5))
    flat_6b = np.zeros(5*12*3)

    bat_deg_cost = np.concatenate((flat_1,line1, flat_2, line2, flat_3, line3, flat_4, line4, flat_5, line5, flat_6a,flat_6b  ) )

    return bat_deg_cost




def create_x_axis():

    time = range(0,1440,1)
    base = datetime(year=2000,month=3,day=17)
    arr_min = np.array([base + timedelta(minutes=i) for i in time])

    time = range(0,1440,60)
    base = datetime(year=2000,month=3,day=17)
    arr_hr = np.array([base + timedelta(minutes=i) for i in time])

    x_hr=[]
    for a in arr_hr:
        x_hr.append(datetime.strftime(a,"%H"))
    print(x_hr)

    return arr_min, arr_hr, x_hr




def charging_current():

    flat_1 = np.zeros(5*12*2)

    line_imp = 100*signal.unit_impulse(5*12*1, 'mid')
    b, a = signal.butter(2, 0.1)
    line_1 = signal.lfilter(b, a, line_imp)
    res_idx = np.where(line_1 < 0)
    line_1[res_idx] = -1*line_1[res_idx]


    line_imp = 1000*signal.unit_impulse(5*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    line2 = signal.lfilter(b, a, line_imp)
    res_idx = np.where(line2 < 0)
    line2[res_idx] = -1*line2[res_idx]

    flat_3 = np.zeros(5*12*2)

    line_imp = 10000*signal.unit_impulse(5*12*3, 'mid')
    b, a = signal.butter(2, 0.001)
    line3 = signal.lfilter(b, a, line_imp)
    res_idx = np.where(line3 < 0)
    line3[res_idx] = -1*line3[res_idx]

    flat_4 = np.zeros(5*12*1)

    line_imp = 1000*signal.unit_impulse(5*12*4, 'mid')
    b, a = signal.butter(2, 0.007)
    line4 = signal.lfilter(b, a, line_imp)
    res_idx = np.where(line4 < 0)
    line4[res_idx] = -1*line4[res_idx]


    flat_5 = np.zeros(5*12*2)

    line_imp = 100*signal.unit_impulse(int(5*12*0.5), 'mid')
    b, a = signal.butter(1, 0.1)
    line5 = signal.lfilter(b, a, line_imp)
    res_idx = np.where(line5 < 0)
    line5[res_idx] = -1*line5[res_idx]


    flat_6a = np.zeros(int(5*12*0.5))
    flat_6b = np.zeros(5*12*3)

    char_current = np.concatenate((flat_1,line_1, line2, flat_3, line3, flat_4, line4, flat_5, line5, flat_6a,flat_6b  ) )


    return char_current


demand = create_demand_impulse()

arr_min,arr_hr,x_hr = create_x_axis()

Minute_Elec_price = create_electricity_price()

bat_deg_cost = battery_degradation_cost()

char_current = charging_current()

print( len(bat_deg_cost) )

# fig,ax = plt.subplots(3)


# ax[0].plot(arr_min, Minute_Elec_price.values())
# #ax[0].ylabel('Electricity price $/MWh')
# ax[1].plot(arr_min, demand)
# ax[2].plot(arr_min, bat_deg_cost)
fig, (ax1, ax2,ax3,ax4) = plt.subplots(4, sharex=True)
plt.xticks(list(arr_hr),x_hr)
plt.xlabel(' Time of day [24-Hour]')
plt.xticks(rotation=90)
plt.margins(0.1, 0.1)


# ax1.plot(arr_min, list(Minute_Elec_price.values()),'r')
# ax1.set(ylabel='Electricity price ($/MWh)')
# ax1.set_facecolor('#eafff5')

# ax2.plot(arr_min, demand,'g')
# ax2.set(ylabel='Customer Demand (#)')
# ax2.set_facecolor('#fbeaff')

# ax3.plot(arr_min, bat_deg_cost,'b')
# ax3.set(ylabel='bat. deg. cost (Ah)')
# ax3.set_facecolor('#feffea')

# ax4.plot(arr_min, char_current,'m')
# ax4.set(ylabel='charging current (A)')
# ax4.set_facecolor('#ffedea')
# plt.pause(0.00000001)

for i in range(0,1440,4):
    ax1.plot(arr_min[0:i], list(Minute_Elec_price.values())[0:i],'r')
    ax1.set(ylabel='Electricity price ($/MWh)')
    ax1.set_facecolor('#eafff5')

    ax2.plot(arr_min[0:i], demand[0:i],'g')
    ax2.set(ylabel='Customer Demand (#)')
    ax2.set_facecolor('#fbeaff')

    ax3.plot(arr_min[0:i], bat_deg_cost[0:i],'b')
    ax3.set(ylabel='bat. deg. cost (Ah)')
    ax3.set_facecolor('#feffea')

    ax4.plot(arr_min[0:i], char_current[0:i],'m')
    ax4.set(ylabel='charging current (A)')
    ax4.set_facecolor('#ffedea')
    plt.pause(0.00000001)


# plt.plot(np.arange(-13, 12), eve_imp)
# plt.plot(np.arange(-13, 12), response)


#plt.grid(True)
plt.show()



