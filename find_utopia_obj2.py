import gurobipy as gp
from gurobipy import GRB
import math




def find_utopia_obj2(num_stab,char_per,t_s,del_t,Imax,Nv,Icmax,SOCdep,SOC_1,Cbat,SOC_xtra):

    m2 = gp.Model('quad_prog')
    m2.params.NonConvex = 2
    m2.reset(0)

    TT2 = []
    for v in range(0,Nv):
        TT2.append( max(math.floor((char_per[v] + t_s) / del_t) , 1)  ) # ceil to give atleast 1 timeslot of char_per < del_t

    max_TT2 = max(TT2) 

    # Decision variable declaration
    I2 = []
    for v in range(0,Nv):
        I2.append( m2.addVars((TT2[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )


    # lower_bound and upper battery power constraint
    bat_pwr_constr_l2 = []
    bat_pwr_constr_u2 = []
    for v in range(0,Nv):
        for i in range(0,TT2[v]): 
            bat_pwr_constr_l2.append( m2.addConstr( I2[v][i] >= 0 ) )
            bat_pwr_constr_u2.append( m2.addConstr( I2[v][i] <= Imax ) )


    # slot power constraint
    for i in range(0,max_TT2):
        slot_pwr2 = []
        for v in range(0,Nv):
            if i < TT2[v]:
                slot_pwr2.append(I2[v][i])
        
        m2.addConstr( sum(slot_pwr2) <= Icmax )

    # lower_bound Energy constraint
    tot_char_curr = []
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT2[v]):
            each_veh_curr.append(I2[v][i])
            tot_char_curr.append(I2[v][i])
        if(TT2[v] > 0):
            m2.addConstr( ( sum(each_veh_curr) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )
            m2.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )


    #like boby variable in smaple code.
    SOC2 = []
    for v in range(0,Nv):
        SOC2.append( m2.addVars((TT2[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

    #constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT2[v]):
            #bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m2.addConstr(SOC2[v][i], GRB.EQUAL, SOC_1[v] + (I2[v][i]* del_t) / Cbat[v])
                #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:
                m2.addConstr(SOC2[v][i], GRB.EQUAL, SOC2[v][i-1] + (I2[v][i]* del_t) / Cbat[v])
                #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)

    # like boby variable in smaple code.
    SOC_avg2 = []
    for v in range(0,Nv):
        SOC_avg2.append( m2.addVars((TT2[v]), vtype=GRB.CONTINUOUS, lb=0, ub=1) )

    # SOC constraint update
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT2[v]):
            #bat_SOC = m.addVar(soc_min,soc_max)
            if first == 1:
                m2.addConstr(SOC_avg2[v][i], GRB.EQUAL, SOC_1[v] + (0.5*(I2[v][i]* del_t)) / Cbat[v])
                #m.addConstr(SOC_1[v], GRB.EQUAL, bat_SOC)
                first = 0
            else:         
                m2.addConstr(SOC_avg2[v][i], GRB.EQUAL, SOC2[v][i-1] + (0.5*(I2[v][i]* del_t)) / Cbat[v])
                #m.addConstr(SOC[v][i], GRB.EQUAL, bat_SOC)


    #####   Paramters of calendric degradation     #####
    ## p1 =   5.387*10**-5 # for 6 min timeslot
    ## p2 =   2.143*10**-5 # for 6 min timeslot
    adj_var = 2 # adjustment variable to push the charging to later
    p1 = 0.0001347
    p2 = 5.356*10**-5


    b4 = []
    b5 = []

    for v in range(0,Nv):
        b4.append( m2.addVars((TT2[v]),vtype=GRB.BINARY) )
        b5.append( m2.addVars((TT2[v]),vtype=GRB.BINARY) )

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

    cap_loss2 = []
    for v in range(0,Nv):
        cap_loss2.append( m2.addVars((TT2[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.05) )
    for v in range(0,Nv):
        for i in range(0,TT2[v]):
            obj4 = m2.addVar(vtype=GRB.CONTINUOUS, name="obj4")
            obj5 = m2.addVar(vtype=GRB.CONTINUOUS, name="obj5")

            m2.addConstr( obj5, GRB.EQUAL, p00b1 + p10b1*SOC_avg2[v][i] + p01b1*(I2[v][i]) + p11b1*SOC_avg2[v][i]*(I2[v][i]) + p02b1*(I2[v][i])**2  + p1*SOC_avg2[v][i]*adj_var + p2 )# + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3 )
            m2.addConstr( obj4,GRB.EQUAL, p00b2 + p10b2*SOC_avg2[v][i] + p01b2*(I2[v][i]) + p11b2*SOC_avg2[v][i]*(I2[v][i]) + p02b2*(I2[v][i])**2  + p1*SOC_avg2[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)

            m2.addConstr(  b4[v][i] + b5[v][i], GRB.EQUAL, 1 ) # b1[v][i] + b2[v][i] + b3[v][i] + b3[v][i] +

            m2.addGenConstrIndicator(b4[v][i], True, I2[v][i] <= 960*SOC_avg2[v][i])
            m2.addGenConstrIndicator(b5[v][i], True, I2[v][i] >= 960*SOC_avg2[v][i])

            m2.addConstr((b5[v][i] == 1) >> (cap_loss2[v][i] ==  obj5), name="indicator_constr1")
            m2.addConstr((b4[v][i] == 1) >> (cap_loss2[v][i] ==   obj4  ), name="indicator_constr2")

    cap_loss_array2 = []
    for v in range(0,Nv):
        for i in range(0,TT2[v]):
            cap_loss_array2.append(cap_loss2[v][i])


    m2.setObjective( sum([num_stab*c for c in cap_loss_array2]), GRB.MINIMIZE)
    m2.update()
    m2.optimize()
    obj2 = m2.getObjective()
    utopia_obj2 = obj2.getValue() # utopia point 
    print(utopia_obj2)

    utopia_I_sol2 = {} # Decision variable, solution at utopia point 
    utopia_SOC_avg_sol2 = {}
    for v in range(0,Nv):
        for i in range(0,TT2[v]):
            utopia_I_sol2[v,i] = I2[v][i].x
            utopia_SOC_avg_sol2[v,i] = SOC_avg2[v][i].x

    return TT2,utopia_obj2, utopia_I_sol2, utopia_SOC_avg_sol2