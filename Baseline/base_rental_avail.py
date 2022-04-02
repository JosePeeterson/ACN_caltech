
import math
import matplotlib.pyplot as plt
import sys

def base_rental_avail_obj(SOC_xtra,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat):

    weights = []

    for v in range(0,Nv):
        for i in range(0,TT[v]): 
            weights.append( 1/(TT[v] + i) )
            #weights.append((-1/TT[v])*i + 1)
            #weights.append(math.exp(-i))

    peak_load_percent = 0.75 # 0 - 1
    peak_per_veh=[0]*Nv
    for v in range(0,Nv):
        for i in range(0,TT[v]): 
            if( I[v][i] >= peak_load_percent*Imax ):
                peak_per_veh[v]+=1


    return weights,peak_per_veh













