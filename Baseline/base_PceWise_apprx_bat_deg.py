
import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil
from numpy import mat

def base_bat_deg_obj(ts_width,SOC_xtra,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
    # WITH taking ln

    begin_time = dateutil.parser.parse(begin_time)


    Tiv = 30 # temperature

    
    ks1 = -4.092*(10**-4)
    ks2 = -2.167 
    ks3 = 1.408*(10**-5)
    ks4 = 6.130

    T = Tiv + 273  # temperature
    Tref = Tiv + 273 # reference temperature
    Ea = 182
    R = 0.0083145


    viz_timev_bat = {v:[] for v in range(0,Nv)}
    #print(curr_time)
    for v in range(0,Nv):
        curr_time = begin_time
        for i in range(0,TT[v]):
            viz_timev_bat[v].append( curr_time )
            curr_time = curr_time + datetime.timedelta(minutes=ts_width)


    curr_coef = 22 # adjustment variable to push the charging to later
    p1 = 0.0001347
    p2 = 5.356*10**-5

    cap_loss = []
    soc = []
    soc_avg = []

    for v in range(0,Nv):
        cap_loss.append([])
        soc.append([])
        soc_avg.append([])
        for i in range(0,TT[v]):
            cap_loss[v].append(0)            
            soc[v].append(0)    
            soc_avg[v].append(0)    

    for v in range(0,Nv):
        first = 1
        for i in range(0,TT[v]):

            if first == 1:
                soc[v][i] = SOC_1[v] + (I[v][i]* del_t) / Cbat[v]
                soc_avg[v][i] = SOC_1[v] + (0.5*(I[v][i]* del_t)) / Cbat[v]
            else:
                soc[v][i], GRB.EQUAL, soc[v][i-1] + (I[v][i]* del_t) / Cbat[v]
                soc_avg[v][i] = soc[v][i-1] + (0.5*(I[v][i]* del_t)) / Cbat[v]
                
            print(soc_avg[v][i])

            cap_loss[v][i] = ( ( ks1*0.5*I[v][i]*(del_t/Cbat[v])*math.exp(ks2*(soc_avg[v][i] + 0.5*I[v][i]*(del_t/Cbat[v]))) + \
            ks3*math.exp(ks4*0.5*I[v][i]*(del_t/Cbat[v])) )*math.exp( (-Ea/R)*( (1/T) - (1/Tref) ) ) )*( I[v][i]*del_t ) + \
            p1*soc_avg[v][i]*curr_coef + p2


    cap_loss_array = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            cap_loss_array.append(cap_loss[v][i])


    return viz_timev_bat,cap_loss


