from MOO_apprx_bat_deg import MOO_bat_deg_obj
from MOO_rental_avail import MOO_rental_avail_obj
from MOO_char_cost import MOO_char_cost_obj
import gurobipy as gp
from gurobipy import GRB
import math
import sys

def mult_obj_opt(Weight,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time,vbat):

    m = gp.Model('moo')
    m.params.NonConvex = 2

    m.params.Presolve = 0
    m.reset(0)

    Imax = 100
    Icmax = Nv*Imax

    t_s = 0

    TT = []
    for v in range(0,Nv):
        TT.append( math.ceil((char_per[v] + t_s) / del_t) )

    max_TT = max(TT) 

    # Decision variable declaration
    I = []
    for v in range(0,Nv):
        I.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )

    max_timeslot = 307
    max_current = 100

    max_avail_val = max_current*Nv
    max_bat_deg = (3.382296793000000*10**-4 )*Nv*max_timeslot
    max_char_cost = 98.37*max_timeslot*Nv*vbat*max_current*del_t
    
    W1 = Weight[0]
    W2 = Weight[1]
    W3 = Weight[2]

    WEPV,viz_WEPV, viz_timev_cost  = MOO_char_cost_obj(m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time)

    cap_loss_array,viz_timev_bat  = MOO_bat_deg_obj(m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time)

    tot_char_curr, weights = MOO_rental_avail_obj(m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat)

    m.ModelSense = GRB.MINIMIZE

    # use minimum weight of 10,000 for outright domination to be noticeable
    m.setObjectiveN(  (1/max_char_cost)*sum([a*b*vbat for a,b in zip(tot_char_curr,WEPV)]) ,0,weight = W1)
    m.setObjectiveN(  (1/max_bat_deg)*sum( cap_loss_array) ,1,weight = W2)
    m.setObjectiveN( -1*(1/max_avail_val)*(sum([a*b for a,b in zip(tot_char_curr,weights)]) )  ,2,weight = W3, reltol=0.1 )

    
    m.update()

    m.optimize()

    obj1 = m.getObjective(0)
    ob1 = obj1.getValue()
    obj2 = m.getObjective(1)
    ob2 = obj2.getValue()
    obj3 = m.getObjective(2)
    ob3 = obj3.getValue()

    print('\n')

    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i].x
            #I_temp.append([v,i,I[v][i].x])

    # Status checking
    status = m.Status
    if status in (GRB. INF_OR_UNBD , GRB. INFEASIBLE , GRB. UNBOUNDED ):
        print("The model cannot be solved because it is infeasible or unbounded ")
        sys. exit (1)
    if status != GRB.OPTIMAL:
        print ("Optimization was stopped with status" + str( status ))
        sys. exit (1)



    return TT, I_temp, viz_timev_bat, viz_WEPV, viz_timev_cost, ob1, ob2, ob3,max_TT








































