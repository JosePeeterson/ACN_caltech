import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil

def bat_deg_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
    # WITH taking ln

    begin_time = dateutil.parser.parse(begin_time)
    # Tdep = [10,4,8]
    # del_t = 2  # currently in hours.

    t_s = 0

    Imax = 80
    Icmax = Nv*80


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

    I_lim = 0

    # calendric ageing 

    Qnom = Cbat
    time = [267, 478, 790] #t is in days
    ln_cap_loss = [] # ln_cap_loss is ln(cap_loss - Qnom)

    T = Tiv + 273  # temperature
    Tref = Tiv + 273 # reference temperature
    Ea = 182
    Eb = 52.1
    R = 0.0083145
    ka = 0.0000439
    kb = 0.00101
    idle_time = del_t*(1/24) # time when it is experiencing the SOC in days




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
    #m.params.NonConvex = 2

    m.params.Presolve = 0
    m.reset(0)
    # Decision variable declaration
    I = []
    for v in range(0,Nv):
        I.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )


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





    # like boby variable in sample code.
    Ah_iv = []
    for v in range(0,Nv):
        Ah_iv.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    # Crate_iv constraint update
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
            m.addConstr(Ah_iv[v][i], GRB.EQUAL, (I[v][i]* del_t)*100 )



    Ah_log = []
    for v in range(0,Nv):
        Ah_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    temp_ah = []
    for v in range(0,Nv):
        temp_ah.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )


    for v in range(0,Nv):
        for i in range(0,TT[v]):
            temp_ah[v][i] == Ah_iv[v][i] + I_lim
            #m.addGenConstrLog(temp_ah[v][i], Ah_log[v][i])
            m.addGenConstrLog(Ah_iv[v][i], Ah_log[v][i])


    # like boby variable in smaple code.
    SOC = []
    for v in range(0,Nv):
        SOC.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    #constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT[v]):
            bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m.addConstr(SOC[v][i], GRB.EQUAL, SOC_1[v] + (I[v][i]* del_t) / Cbat[v])
                m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:
                m.addConstr(SOC[v][i], GRB.EQUAL, SOC[v][i-1] + (I[v][i]* del_t) / Cbat[v])
                m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)


    # like boby variable in smaple code.
    SOC_avg = []
    for v in range(0,Nv):
        SOC_avg.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    # SOC constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT[v]):
            bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC_1[v] + (0.5*(I[v][i]* del_t)) / Cbat[v])
                m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:         
                m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC[v][i-1] + (0.5*(I[v][i]* del_t)) / Cbat[v])
                m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)


    # like boby variable in smaple code.
    SOC_dev = []
    for v in range(0,Nv):
        SOC_dev.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    # SOC constraint update
    for v in range(0,Nv):
        for i in range(0,TT[v]):        
            #m.addConstr(SOC_dev[v][i], GRB.EQUAL, ((0.75*I[v][i]*I[v][i]*del_t)/ Cbat**2) - ((0.5*I[v][i]*I[v][i]*(del_t**2))/ Cbat**2)   )
            m.addConstr(SOC_dev[v][i], GRB.EQUAL, (0.5*I[v][i]* del_t)/Cbat[v] )



    exp1 = []
    for v in range(0,Nv):
        exp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    temp1 = []
    for v in range(0,Nv):
        temp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")

            temp1[v][i] == ks2*(SOC_avg[v][i])
            m.addGenConstrExp(temp1[v][i], exp1[v][i])



    exp2 = []
    for v in range(0,Nv):
        exp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    temp2 = []
    for v in range(0,Nv):
        temp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
            temp2[v][i] == ks4*(SOC_dev[v][i]) 
            m.addGenConstrExp(temp2[v][i], exp2[v][i])





    nat_log = []
    for v in range(0,Nv):
        nat_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    temp3 = []
    for v in range(0,Nv):
        temp3.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")

            temp3[v][i] == (ks1*(SOC_dev[v][i])*exp1[v][i] + ks3*exp2[v][i])*100
            m.addGenConstrLog(temp3[v][i], nat_log[v][i])





    nat_log2 = []
    for v in range(0,Nv):
        nat_log2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    temp4 = []
    for v in range(0,Nv):
        temp4.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")

            temp4[v][i] == ( ( (SOC[v][i]*ka*(math.exp( (-Ea/R)*(1/T - 1/Tref) ) ) + kb*math.exp((-Eb/R )*(1/T - 1/Tref) ) )*5*idle_time + Qnom[v] ) / Qnom[v] )*100 
            m.addGenConstrLog(temp4[v][i], nat_log2[v][i])








    # Battery degradation cost Objective #2

    Ah_array = []
    nat_log_array = []
    nat_log_array2 = []


    for v in range(0,Nv):
        for i in range(0,TT[v]):
            Ah_array.append(Ah_log[v][i])
            nat_log_array.append(nat_log[v][i])
            nat_log_array2.append(nat_log2[v][i])

    #+   nat_log_array nat_log_array2  +
    m.setObjective( sum(  Ah_array ), GRB.MINIMIZE)
    #m.setObjective( sum(B_array + Ah_array + Crate_array + b1_array + SOC_array + d_array + a1_a2_array), GRB.MINIMIZE)

    m.update()
    m.optimize()

    #m.printQuality()

    print('\n')

    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i].x
            #I_temp.append([v,i,I[v][i].x])

    
    status = m.Status
    if status in (GRB. INF_OR_UNBD , GRB. INFEASIBLE , GRB. UNBOUNDED ):
        print("The model cannot be solved because it is infeasible or unbounded ")
        sys.exit(1)
    if status != GRB.OPTIMAL:
        print ("Optimization was stopped with status" + str( status ))
        sys.exit(1)

    print(I_temp)

    return TT, I_temp, viz_timev 


