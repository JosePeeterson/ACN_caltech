import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil

def MOO_bat_deg_obj(SOC_xtra,m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
    # WITH taking ln

    begin_time = dateutil.parser.parse(begin_time)
    # Tdep = [10,4,8]
    # del_t = 2  # currently in hours.

    t_s = 0




    # Cbat = 20
    # SOCdep = [0.8, 0.6, 0.7]
    # SOC_1 = [0.1, 0.2, 0.1]
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

    #I_lim = 1
    one = 1

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






    viz_timev_bat = {v:[] for v in range(0,Nv)}
    #print(curr_time)
    for v in range(0,Nv):
        curr_time = begin_time
        for i in range(0,TT[v]):
            viz_timev_bat[v].append( curr_time )
            curr_time = curr_time + datetime.timedelta(minutes=6)






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




    #####   Paramters of calendric degradation     #####
    ## p1 =   5.387*10**-5 # for 6 min timeslot
    ## p2 =   2.143*10**-5 # for 6 min timeslot
    adj_var = 1 # adjustment variable to push the charging to later
    p1 = 0.0001347
    p2 = 5.356*10**-5


    #####   Paramters of degradation due to current    #####
    q1 =  -0.0001528
    q2 =   0.0002643
    q3 =   1.134e-05


    b4 = []
    b5 = []

    for v in range(0,Nv):
        b4.append( m.addVars((TT[v]),vtype=GRB.BINARY) )
        b5.append( m.addVars((TT[v]),vtype=GRB.BINARY) )

    #####   Paramters of cyclic degradation, piecewise  objectives   #####
    p00b1 = 4.169*10**-6    
    p10b1 = -9.871*10**-5
    p01b1 = 1.63*10**-6
    p11b1 = 2.661*10**-6
    p02b1 = -5.757*10**-9

    p00b2 = 6.886*10**-6    
    p10b2 = -1.075*10**-5   
    p01b2 = 1.361*10**-6
    p11b2 = 6.348*10**-7
    p02b2 = -1.902*10**-10

    cap_loss = []
    for v in range(0,Nv):
        cap_loss.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.05) )
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            obj4 = m.addVar(vtype=GRB.CONTINUOUS, name="obj4")
            obj5 = m.addVar(vtype=GRB.CONTINUOUS, name="obj5")

            m.addConstr( obj5, GRB.EQUAL, p00b1 + p10b1*SOC_avg[v][i] + p01b1*(I[v][i]) + p11b1*SOC_avg[v][i]*(I[v][i]) + p02b1*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )# + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3 )
            m.addConstr( obj4,GRB.EQUAL, p00b2 + p10b2*SOC_avg[v][i] + p01b2*(I[v][i]) + p11b2*SOC_avg[v][i]*(I[v][i]) + p02b2*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)

            m.addConstr(  b4[v][i] + b5[v][i], GRB.EQUAL, 1 ) # b1[v][i] + b2[v][i] + b3[v][i] + b3[v][i] +

            m.addGenConstrIndicator(b4[v][i], True, I[v][i] <= 960*SOC_avg[v][i])
            m.addGenConstrIndicator(b5[v][i], True, I[v][i] >= 960*SOC_avg[v][i])

            m.addConstr((b5[v][i] == 1) >> (cap_loss[v][i] ==  obj5), name="indicator_constr1")
            m.addConstr((b4[v][i] == 1) >> (cap_loss[v][i] ==   obj4  ), name="indicator_constr2")







    cap_loss_array = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            cap_loss_array.append(cap_loss[v][i])



    return cap_loss_array,viz_timev_bat






################# OLD CODE BELOW FOR THE ACTUAL MODEL INSTEAD OF APPROX. ################
#########################################################################################


# import gurobipy as gp
# from gurobipy import GRB
# import math
# import sys
# import datetime
# import dateutil

# def MOO_bat_deg_obj(m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time):
#     # WITH taking ln

#     begin_time = dateutil.parser.parse(begin_time)
#     # Tdep = [10,4,8]
#     # del_t = 2  # currently in hours.

#     t_s = 0




#     # Cbat = 20
#     # SOCdep = [0.8, 0.6, 0.7]
#     # SOC_1 = [0.1, 0.2, 0.1]
#     SOC_xtra = 0.001
#     soc_min = 0
#     soc_max = 1

#     Tiv = 30 # temperature
#     #R = 8.3145

#     # ks1 = -1.917*(10**-5)
#     # ks2 = 9.241
#     # ks3 = 8.11*(10**-6)
#     # ks4 = 9.975

#     # ks1 = 1
#     # ks2 = 1
#     # ks3 = 1
#     # ks4 = 1
    
#     ks1 = -4.092*(10**-4)
#     ks2 = -2.167 
#     ks3 = 1.408*(10**-5)
#     ks4 = 6.130

#     #I_lim = 1
#     one = 1

#     # calendric ageing 

#     Qnom = Cbat
#     time = [267, 478, 790] #t is in days
#     ln_cap_loss = [] # ln_cap_loss is ln(cap_loss - Qnom)

#     T = Tiv + 273  # temperature
#     Tref = Tiv + 273 # reference temperature
#     Ea = 182
#     Eb = 52.1
#     R = 0.0083145
#     ka = 0.0000439
#     kb = 0.00101
#     idle_time = del_t*(1/24) # time when it is experiencing the SOC in days






#     viz_timev_bat = {v:[] for v in range(0,Nv)}
#     #print(curr_time)
#     for v in range(0,Nv):
#         curr_time = begin_time
#         for i in range(0,TT[v]):
#             viz_timev_bat[v].append( curr_time )
#             curr_time = curr_time + datetime.timedelta(minutes=6)






#     # upper_bound battery power constraint
#     bat_pwr_constr_l = []
#     for v in range(0,Nv):
#         for i in range(0,TT[v]): 
#             bat_pwr_constr_l.append( m.addConstr( I[v][i] >= 0 ) )

#     # lower_bound battery power constraint
#     bat_pwr_constr_u = []
#     for v in range(0,Nv):
#         for i in range(0,TT[v]): 
#             bat_pwr_constr_u.append( m.addConstr( I[v][i] <= Imax ) )


#     # slot power constraint
#     for i in range(0,max_TT):
#         slot_pwr = []
#         for v in range(0,Nv):
#             if i < TT[v]:
#                 slot_pwr.append(I[v][i])
        
#         m.addConstr( sum(slot_pwr) <= Icmax )

#     # lower_bound Energy constraint
#     tot_char_curr = []
#     for v in range(0,Nv):
#         each_veh_curr = []
#         for i in range(0,TT[v]):
#             each_veh_curr.append(I[v][i])
#             tot_char_curr.append(I[v][i])
#         if(TT[v] > 0):
#             m.addConstr( ( sum(each_veh_curr) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )
#             print(v,i)

#     # upper_bound Energy constraint
#     for v in range(0,Nv):
#         each_veh_curr = []
#         for i in range(0,TT[v]):
#             each_veh_curr.append(I[v][i])
#         if(TT[v] > 0):
#             m.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )
#             print(v,i)




#     '''
#     # like boby variable in sample code.
#     Ah_iv = []
#     for v in range(0,Nv):
#         Ah_iv.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

#     # Crate_iv constraint update
#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
#             m.addConstr(Ah_iv[v][i], GRB.EQUAL, (I[v][i]* del_t)*100 )
#     '''


#     Ah_log = []
#     for v in range(0,Nv):
#         Ah_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=2) )

#     temp_ah = []
#     for v in range(0,Nv):
#         temp_ah.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS,lb=0, ub=Imax*del_t) )


#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             m.addConstr(temp_ah[v][i], GRB.EQUAL, (I[v][i]*del_t) + one )
#             #m.addConstr(temp_ah[v][i], GRB.EQUAL, (I[v][i]*del_t) + I_lim)
#             #temp_ah[v][i] == Ah_iv[v][i] + I_lim
#             #m.addGenConstrLog(temp_ah[v][i], Ah_log[v][i])
#             m.addGenConstrLog(temp_ah[v][i], Ah_log[v][i])


#     # like boby variable in smaple code.
#     SOC = []
#     for v in range(0,Nv):
#         SOC.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

#     #constraint update
#     for v in range(0,Nv):
#         first = 1
#         for i in range(0,TT[v]):
#             #bat_SOC = m.addVar(soc_min,soc_max)
#             if first == 1:
#                 m.addConstr(SOC[v][i], GRB.EQUAL, SOC_1[v] + (I[v][i]* del_t) / Cbat[v])
#                 #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
#                 first = 0
#             else:
#                 m.addConstr(SOC[v][i], GRB.EQUAL, SOC[v][i-1] + (I[v][i]* del_t) / Cbat[v])
#                 #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)


#     # like boby variable in smaple code.
#     SOC_avg = []
#     for v in range(0,Nv):
#         SOC_avg.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

#     # SOC constraint update
#     for v in range(0,Nv):
#         first = 1
#         for i in range(0,TT[v]):
#             #bat_SOC = m.addVar(soc_min,soc_max)
#             if first == 1:
#                 m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC_1[v] + (0.5*(I[v][i]* del_t)) / Cbat[v])
#                 #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
#                 first = 0
#             else:         
#                 m.addConstr(SOC_avg[v][i], GRB.EQUAL, SOC[v][i-1] + (0.5*(I[v][i]* del_t)) / Cbat[v])
#                 #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)


#     # like boby variable in smaple code.
#     SOC_dev = []
#     for v in range(0,Nv):
#         SOC_dev.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

#     # SOC constraint update
#     for v in range(0,Nv):
#         for i in range(0,TT[v]):        
#             #m.addConstr(SOC_dev[v][i], GRB.EQUAL, ((0.75*I[v][i]*I[v][i]*del_t)/ Cbat**2) - ((0.5*I[v][i]*I[v][i]*(del_t**2))/ Cbat**2)   )
#             m.addConstr(SOC_dev[v][i], GRB.EQUAL, (0.5*I[v][i]* del_t)/Cbat[v] )



#     exp1 = []
#     for v in range(0,Nv):
#         exp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

#     temp1 = []
#     for v in range(0,Nv):
#         temp1.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=-3, ub=0) )

#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
#             m.addConstr(temp1[v][i], GRB.EQUAL, ks2*SOC_avg[v][i] )
#             m.addGenConstrExp(temp1[v][i], exp1[v][i])



#     exp2 = []
#     for v in range(0,Nv):
#         exp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=1, ub=1097) )

#     temp2 = []
#     for v in range(0,Nv):
#         temp2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=7) )

#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
#             m.addConstr(temp2[v][i], GRB.EQUAL, ks4*(SOC_dev[v][i]) )
#             m.addGenConstrExp(temp2[v][i], exp2[v][i])



#     inverter = 12

#     nat_log = []
#     for v in range(0,Nv):
#         nat_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb = -10, ub = 0) )
#         #nat_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb = -100, ub = -3) )

#     temp3 = []
#     for v in range(0,Nv):
#         temp3.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb = 0, ub = 0.016) )
#     log_adj = []
#     for v in range(0,Nv):
#         log_adj.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb = -10, ub = 80) )
#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
#             #m.addConstr(temp3[v][i], GRB.EQUAL, ks1*(SOC_dev[v][i])*exp1[v][i] + ks3*exp2[v][i] + 0.0004, 'quad'+str((v+1)*i) )
#             m.addConstr(temp3[v][i], GRB.EQUAL, ks1*(SOC_dev[v][i])*exp1[v][i] + ks3*exp2[v][i] + 0.0008, 'quad'+str((v+1)*i) )
#             m.addGenConstrLog(temp3[v][i], nat_log[v][i])
#             m.addConstr(log_adj[v][i], GRB.EQUAL, inverter + nat_log[v][i])





#     # nat_log2 = []
#     # for v in range(0,Nv):
#     #     nat_log2.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

#     # temp4 = []
#     # for v in range(0,Nv):
#     #     temp4.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS) )

#     # for v in range(0,Nv):
#     #     for i in range(0,TT[v]):
#     #         #bat_vbat = m.addVar(vbat_min,vbat_max,name="bat_SOC")
#     #         m.addConstr(temp4[v][i] , GRB.EQUAL,   (SOC[v][i]*ka*(1000000 ) + kb )*5*idle_time + Qnom[v]  )
#     #         #temp4[v][i] == ( ( (SOC[v][i]*ka*(math.exp( (-Ea/R)*(1/T - 1/Tref) ) ) + kb*math.exp((-Eb/R )*(1/T - 1/Tref) ) )*5*idle_time + Qnom[v] ) / Qnom[v] )*100 
#     #         m.addGenConstrLog(temp4[v][i], nat_log2[v][i])








#     # Battery degradation cost Objective #2

#     Ah_array = []
#     #nat_log_array = []
#     #nat_log_array2 = []
#     log_adj_array = []


#     for v in range(0,Nv):
#         for i in range(0,TT[v]):
#             Ah_array.append(Ah_log[v][i])
#             #nat_log_array.append(nat_log[v][i])
#             #nat_log_array2.append(nat_log2[v][i])
#             log_adj_array.append(log_adj[v][i])


#     return Ah_array,viz_timev_bat, log_adj_array







