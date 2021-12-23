import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil

def apprx_curr_bat_deg_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
    # WITH taking ln

    begin_time = dateutil.parser.parse(begin_time)
    # Tdep = [10,4,8]
    # del_t = 2  # currently in hours.

    t_s = 0

    Imax = 100
    Icmax = Nv*Imax


    # Cbat = 20
    # SOCdep = [0.8, 0.6, 0.7]
    # SOC_1 = [0.1, 0.2, 0.1]
    SOC_xtra = 0.01






    TT = []
    for v in range(0,Nv):
        TT.append( math.ceil((char_per[v] + t_s) / del_t) )

    max_TT = max(TT) 

    viz_timev = {v:[] for v in range(0,Nv)}
    #print(curr_time)
    for v in range(0,Nv):
        curr_time = begin_time
        for i in range(0,TT[v]):
            viz_timev[v].append( curr_time )
            curr_time = curr_time + datetime.timedelta(minutes=6)


    m = gp.Model('bat_deg')
    m.params.NonConvex = 2

    m.params.Presolve = 0
    m.reset(0)
    # Decision variable declaration
    I = []
    for v in range(0,Nv):
        I.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )


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
            m.addConstr( ( sum(each_veh_curr) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )
            print(v,i)

    # upper_bound Energy constraint
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
        if(TT[v] > 0):
            m.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )
            print(v,i)



    a1 =   0.0001327
    b1 =      0.1454 
    c1 =   -0.000114 
    d1 =      -1.865 


    p1 =  -4.618e-05
    p2 =   0.0001597
    p3 =   2.621e-05

    # #####   Paramters of caledric degradation     ##### 
    # p1 =   5.387*10**-5
    # p2 =   2.143*10**-5
    # adj_var = 5 # adjustment variable to push the charging to later

    cap_loss = []
    for v in range(0,Nv):
        cap_loss.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.05) )

    temp1 = []
    for v in range(0,Nv):
        temp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.2) )
    
    temp2 = []
    for v in range(0,Nv):
        temp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=-0.7, ub=0) )

    exp1 = []
    for v in range(0,Nv):
        exp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=1, ub=1.3) )

    exp2 = []
    for v in range(0,Nv):
        exp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            m.addConstr( cap_loss[v][i], GRB.EQUAL, p1*(I[v][i]/Cbat[v])**2 + p2*(I[v][i]/Cbat[v]) + p3 )
            #bat_SOC = m.addVar(soc_min,soc_max)
            #cap_loss = p00 + p10*SOC_avg[v][i] + p01*(I[v][i]) + p11*SOC_avg*(I[v][i]) + p02*(I[v][i])**2
            # m.addConstr( temp1[v][i], GRB.EQUAL, b1*(I[v][i]/Cbat[v]) )
            # m.addConstr( temp2[v][i], GRB.EQUAL, d1*(I[v][i]/Cbat[v]) )
            # m.addGenConstrExp( temp1[v][i], exp1[v][i])
            # m.addGenConstrExp(temp2[v][i],exp2[v][i])
            # m.addConstr( cap_loss[v][i], GRB.EQUAL, a1*exp1[v][i] + c1*exp2[v][i]  ) #+ p1*SOC_avg[v][i]*adj_var + p2






    max_val = 1#0.00008*Nv*307

    cap_loss_array = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            cap_loss_array.append(cap_loss[v][i])



    #+   nat_log_array nat_log_array2  +
    # sum( nat_log_array) sum(cap_loss_array)
    m.setObjective(  (1/max_val)*sum(cap_loss_array), GRB.MINIMIZE)
    #m.setObjective( sum(B_array + Ah_array + Crate_array + b1_array + SOC_array + d_array + a1_a2_array), GRB.MINIMIZE)

    m.update()
    m.optimize()
    objval = m.ObjVal
    m.write('apprx_bat_deg.lp')
    #m.printQuality()

    print('\n')

    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i].x

    
    status = m.Status
    if status in (GRB. INF_OR_UNBD , GRB. INFEASIBLE , GRB. UNBOUNDED ):
        print("The model cannot be solved because it is infeasible or unbounded ")
        sys.exit(1)
    if status != GRB.OPTIMAL:
        print ("Optimization was stopped with status" + str( status ))
        sys.exit(1)

    print(I_temp)

    return TT, I_temp, viz_timev,objval 


