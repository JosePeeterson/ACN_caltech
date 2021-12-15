import sys
import json
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import colorbar
import pandas as pd
from datetime import date, datetime
from new_rental_avail_obj import optimization
import gurobipy as gp
from gurobipy import GRB
import dateutil
import datetime

def convert_datetime(x):

    t = x[5:-4]
    t1= t[0:2]+ " " + t[3:6] + " " + t[7:11] + " "+ t[12:20]
    format_str = '%d %b %Y %H:%M:%S' # The format
    datetime_obj = datetime.datetime.strptime(t1, format_str)
    return datetime_obj

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


with open('ACN_DATA/acndata_sessions (7).json') as f:
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
    con_time_dt = []
    discon_time = []
    discon_time_dt = []
    kw_req = []
    kw_del = []
    all_time_one_space_data = {}
    for i in range(0, len_events):
        if ( (data['_items'][i]['spaceID'] == j) ):            
            if ( data['_items'][i]['userInputs'] != None):
                dx = data['_items'][i]['disconnectTime']
                discon_time.append(dx)
                discon_time_dt.append(convert_datetime(dx))
                for l in range(0,len(data['_items'][i]['userInputs']) ):
                    cx = data['_items'][i]['userInputs'][l]["modifiedAt"]
                    con_time.append(cx)
                    con_time_dt.append(convert_datetime(cx))
                    kw_req.append(data['_items'][i]['userInputs'][l]['kWhRequested'])
                    kw_del.append(data['_items'][i]['userInputs'][l]['minutesAvailable'])


    all_time_one_space_data['kWhRequested'] = kw_req
    all_time_one_space_data['Connect_time'] = con_time
    all_time_one_space_data['Disconnect_time'] = discon_time
    all_time_one_space_data['Connect_time_datetime'] = con_time_dt
    all_time_one_space_data['Disconnect_time_datetime'] = discon_time_dt
    
    all_time_one_space_data['Minutes_available'] = kw_del
    All_space_data[j] = all_time_one_space_data
    #print(j)

each_veh_connect_times = []
unique_connect_time_dates = []

col_con = ['bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo','ko','wo','bo','go','ro','co','mo','yo','ko','wo']
col_disc = ['bx','gx','rx','cx','mx','yx','kx','wx','bx','gx','rx','cx','mx','yx','kx','wx','bx','gx','rx','cx','mx','yx','kx','wx','bx','gx','rx','cx','mx','yx','kx','wx']

fig, ax1 = plt.subplots()

print(len(unique_space_id))

for v,j in enumerate(unique_space_id):

    x1 = All_space_data[j]['Connect_time_datetime']
    x2 = All_space_data[j]['Disconnect_time_datetime']   

    ax1.plot(x1,[v]*len(x1),col_con[v])
    ax1.plot(x2,[v]*len(x2),col_disc[v])

plt.show()

    # print(date)
    # format_str = '%d/%m/%Y %H:%M:%S' # The format
    # datetime_obj = datetime.datetime.strptime(date, format_str)
    # print(str(datetime_obj.date()))
    