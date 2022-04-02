import math as m
from time import strptime
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from datetime import datetime
from datetime import datetime, timedelta 
import sys

def create_demand_impulse():

    flat_res = np.zeros(5*12*7)

    morn_imp = 20*signal.unit_impulse(2*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    morn_response = signal.lfilter(b, a, morn_imp)
    res_idx = np.where(morn_response < 0)
    morn_response[res_idx] = -1*morn_response[res_idx]

    flat_res1 = np.zeros(5*12*3)

    noon_imp = 20*signal.unit_impulse(2*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    noon_response = signal.lfilter(b, a, noon_imp)
    res_idx = np.where(noon_response < 0)
    noon_response[res_idx] = -1*noon_response[res_idx]

    flat_res2 = np.zeros(5*12*3)

    eve_imp = 20*signal.unit_impulse(3*12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    eve_response = signal.lfilter(b, a, eve_imp)
    res_idx = np.where(eve_response < 0)
    eve_response[res_idx] = -1*eve_response[res_idx]

    eve_imp = 10*signal.unit_impulse(12*5, 'mid')
    b, a = signal.butter(2, 0.01)
    eve_response1 = signal.lfilter(b, a, eve_imp)
    res_idx1 = np.where(eve_response1 < 0)
    eve_response1[res_idx1] = -1*eve_response1[res_idx1]

    flat_res3 = np.zeros(5*12*3)

    demand = np.concatenate((flat_res, morn_response, flat_res1, noon_response, \
        flat_res2,  eve_response, eve_response1, flat_res3))

    return demand


demand = create_demand_impulse()

print(len(demand))

time = range(0,1440,1)
base = datetime(year=2000,month=1,day=1)
arr_min = np.array([base + timedelta(minutes=i) for i in time])


time = range(0,1440,60)
base = datetime(year=2000,month=1,day=1)
arr_hr = np.array([base + timedelta(minutes=i) for i in time])

x_hr=[]
for a in arr_hr:
    x_hr.append(datetime.strftime(a,"%H"))
print(x_hr)

import matplotlib.pyplot as plt
plt.plot(arr_min, demand)
plt.xticks(list(arr_hr),x_hr)
plt.xticks(rotation=90)
# plt.plot(np.arange(-13, 12), eve_imp)
# plt.plot(np.arange(-13, 12), response)
plt.margins(0.1, 0.1)
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
#plt.grid(True)
plt.show()


sys.exit()

time = range(0,1440,5)

base = datetime(2000, 1, 1)
arr = np.array([base + timedelta(minutes=i) for i in time])

#print(arr)
print(len(arr))




import matplotlib.pyplot as plt
plt.plot(np.arange(-25, 24), eve_imp)
plt.plot(np.arange(-25, 24), response)
# plt.plot(np.arange(-13, 12), eve_imp)
# plt.plot(np.arange(-13, 12), response)
plt.margins(0.1, 0.1)
plt.xlabel('Time [samples]')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()


doub_res = np.append(response,response)




x = np.arange(0,10,0.1)
print(x)
y = np.sin(x) + 1

# plt.plot(x,y)
# plt.show()

imp1 = signal.unit_impulse(1440, 'mid')

imp = signal.unit_impulse(1440, 'mid')
# for i in range(0,10):

d = signal.unit_impulse(1440, 2)

imp = signal.unit_impulse(1440, 'mid')

imp = signal.unit_impulse(1440, 'mid')
b, a = signal.butter(4, 0.2)
response = signal.lfilter(b, a, imp)
print(type(response))

res1 = np.where(response < 0)
response[res1] = -1*response[res1]

doub_res = np.append(response,response)

doub_imp = np.append(imp,imp)


    
print(time)





