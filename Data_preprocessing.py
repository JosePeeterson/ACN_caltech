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
from cal_deg_obj import cal_bat_deg_optimization
from cyc_deg_obj import cyc_bat_deg_optimization
from apprx_cyc_bat_deg_obj import apprx_cyc_bat_deg_optimization
from apprx_cal_bat_deg_obj import apprx_cal_bat_deg_optimization
import numpy as np
from apprx_total_bat_deg_obj import apprx_tot_bat_deg_optimization
from apprx_curr_bat_deg import apprx_curr_bat_deg_optimization


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


with open('ACN_DATA/acndata_6_months.json') as f:
    data = json.load(f)

len_events = len(data['_items'])

#print(len_events)

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
        if ( (data['_items'][i]['spaceID'] == j) and (data['_items'][i]['userInputs'] != None) ):
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
    # for i in range(0,len(All_space_data[s]['kWhRequested'])):
    #     i
        #print(All_space_data[s]['kWhRequested'][i], All_space_data[s]['Connect_time'][i])
        #print(len(All_space_data[s]['Minutes_available']))
        #print(len(All_space_data[s]['Disconnect_time']))
        #print(All_space_data[s]['Connect_time'])
    #print('\n')
    for d in All_space_data[s]['Connect_time']:
        date = d[5:16]
        if (date not in unique_connect_time_dates):
            unique_connect_time_dates.append(date)

print(unique_connect_time_dates)
