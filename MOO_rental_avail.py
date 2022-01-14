import gurobipy as gp
from gurobipy import GRB
import math
import matplotlib.pyplot as plt
import sys

def MOO_rental_avail_obj(m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat):

    #Nv = 3
    #Tdep = [10,4,8]
    #del_t = 0.6 # every 6 minutes, in hours  
    t_s = 0

 


    #Cbat = 270
    #Ebat = 300
    #SOCdep = [0.8, 0.6, 0.7]
    #SOC_1 = [0.1, 0.2, 0.1]
    SOC_xtra = 0.001


    #print(TT)
    
    #def weight_function(i,v):
    #    return 1/(TT[v] + i)


    weights = []


    for v in range(0,Nv):
        for i in range(0,TT[v]): 
            weights.append(( 1/(TT[v] + i) ))
            #weights.append((-1/TT[v])*i + 1)
            #weights.append(math.exp(-i))







    #print(I[1],"\n")
    #print(I[2],"\n")

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
    tot_char_curr = []
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
            tot_char_curr.append(I[v][i])
        if(TT[v] > 0):
            #print(v)
            #print(SOCdep[v],SOC_1[v],Cbat[v])
            m.addConstr( ( sum(each_veh_curr) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )


    # upper_bound Energy constraint
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
        if(TT[v] > 0):
            m.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra )*Cbat[v] )


    return tot_char_curr, weights













