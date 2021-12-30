import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil

def apprx_tot_bat_deg_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
    # WITH taking ln

    begin_time = dateutil.parser.parse(begin_time)
    # Tdep = [10,4,8]
    # del_t = 2  # currently in hours.

    t_s = 0

    Imax = 120
    Icmax = Nv*Imax


    # Cbat = 20
    # SOCdep = [0.8, 0.6, 0.7]
    # SOC_1 = [0.1, 0.2, 0.1]
    SOC_xtra = 0.01
    soc_min = 0 
    soc_max = 1

    Tiv = 30 # temperature
    #R = 8.3145

    # ks1 = -1.917*(10**-5)
    # ks2 = 9.241
    # ks3 = 8.11*(10**-6)
    # ks4 = 9.975

    # ks1 = 1
    # ks2 = 1
    # ks3 = 1
    # ks4 = 1
    
    ks1 = -4.092*(10**-4)
    ks2 = -2.167 
    ks3 = 1.408*(10**-5)
    ks4 = 6.130

    one = 1

    # calendric ageing 

    time = [267, 478, 790] #t is in days
    ln_cap_loss = [] # ln_cap_loss is ln(cap_loss - Qnom)




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



    #like boby variable in smaple code.
    SOC = []
    for v in range(0,Nv):
        SOC.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

    #constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT[v]):
            #bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m.addConstr(SOC[v][i], GRB.EQUAL, SOC_1[v] + (I[v][i]* del_t) / Cbat[v])
                #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:
                m.addConstr(SOC[v][i], GRB.EQUAL, SOC[v][i-1] + (I[v][i]* del_t) / Cbat[v])
                #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)

        # like boby variable in smaple code.
    SOC_avg = []
    for v in range(0,Nv):
        SOC_avg.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

    # SOC constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT[v]):
            #bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC_1[v] + (0.5*(I[v][i]* del_t)) / Cbat[v])
                #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:         
                m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC[v][i-1] + (0.5*(I[v][i]* del_t)) / Cbat[v])
                #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)

    max_time_slot = 466
    #####   Paramters of cyclic degradation     #####
    max_bat_deg = (3.382296793000000*10**-4 )*Nv*max_time_slot # cyc + cal included
    p00 =   1.038*10**-5
    p10 =  -2.003*10**-5
    p01 =   1.281*10**-6
    p11 =   9.554*10**-7
    p02 =  -1.124*10**-9
    div_fac = 2.2

    #####   Paramters of calendric degradation     #####
    p1 =   5.387*10**-5
    p2 =   2.143*10**-5
    adj_var = 3 # adjustment variable to push the charging to later

    #####   Paramters of degradation due to current    #####
    q1 =  -0.0001528
    q2 =   0.0002643
    q3 =   1.134e-05



    cap_loss = []
    for v in range(0,Nv):
        cap_loss.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.05) )


    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_SOC = m.addVar(soc_min,soc_max)
            m.addConstr(cap_loss[v][i], GRB.EQUAL, ( (p00 + p10*SOC_avg[v][i] + p01*(I[v][i]+20) + p11*SOC_avg[v][i]*(I[v][i]+20) + p02*(I[v][i]+20)**2)/div_fac + p1*SOC_avg[v][i]*adj_var + p2   ) ) #+ q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3
            #cap_loss = p00 + p10*SOC_avg[v][i] + p01*(I[v][i]) + p11*SOC_avg*(I[v][i]) + p02*(I[v][i])**2



    cap_loss_array = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            cap_loss_array.append(cap_loss[v][i])



    #+   nat_log_array nat_log_array2  +
    # sum( nat_log_array) sum(cap_loss_array)
    m.setObjective(  (1/max_bat_deg)*sum(cap_loss_array), GRB.MINIMIZE)
    #m.setObjective( sum(B_array + Ah_array + Crate_array + b1_array + SOC_array + d_array + a1_a2_array), GRB.MINIMIZE)

    m.update()
    m.optimize()

    m.write('apprx_bat_deg.lp')
    #m.printQuality()
    objval = m.ObjVal
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

    return TT, I_temp, viz_timev, objval 


