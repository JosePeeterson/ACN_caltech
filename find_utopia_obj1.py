import gurobipy as gp
from gurobipy import GRB
import math




def find_utopia_obj1(WEPV,Nv,Imax,del_t,t_s,Icmax,SOCdep, char_per, SOC_1, SOC_xtra,Cbat):

    m1 = gp.Model('lin_prog1')
    m1.params.NonConvex = 2
    m1.reset(0)
    num_stab = 1000 # provide numerical stability by avoiding very small coefficients

    TT1 = []
    for v in range(0,Nv):
        TT1.append( max(math.floor((char_per[v] + t_s) / del_t) , 1)  ) # ceil to give atleast 1 timeslot of char_per < del_t

    max_TT1 = max(TT1) 

    # Decision variable declaration
    I1 = []
    for v in range(0,Nv):
        I1.append( m1.addVars((TT1[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )

    # lower and upper_bound battery power constraint
    bat_pwr_constr_l1 = []
    bat_pwr_constr_u1 = []
    for v in range(0,Nv):
        for i in range(0,TT1[v]): 
            bat_pwr_constr_l1.append( m1.addConstr( I1[v][i] >= 0 ) )
            bat_pwr_constr_u1.append( m1.addConstr( I1[v][i] <= Imax ) )

    # slot power constraint
    for i in range(0,max_TT1):
        slot_pwr1 = []
        for v in range(0,Nv):
            if i < TT1[v]:
                slot_pwr1.append(I1[v][i])
        
        m1.addConstr( sum(slot_pwr1) <= Icmax )

    # lower_bound and upper_bound Energy constraint
    tot_char_curr1 = []
    for v in range(0,Nv):
        each_veh_curr1 = []
        for i in range(0,TT1[v]):
            each_veh_curr1.append(I1[v][i])
            tot_char_curr1.append(I1[v][i])
        if(TT1[v] > 0):
            m1.addConstr( ( sum(each_veh_curr1) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )
            m1.addConstr( ( sum(each_veh_curr1) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )


    m1.setObjective( num_stab*sum([a*b for a,b in zip(tot_char_curr1,WEPV)]), GRB.MINIMIZE )
    m1.update()
    m1.optimize()
    obj1 = m1.getObjective()
    utopia_obj1 = obj1.getValue() # utopia point 
    print(utopia_obj1)

    utopia_sol1 = {} # Decision variable, solution at utopia point 
    for v in range(0,Nv):
        for i in range(0,TT1[v]):
            utopia_sol1[v,i] = I1[v][i].x

    return TT1,utopia_obj1, utopia_sol1