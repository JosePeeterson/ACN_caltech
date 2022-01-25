import gurobipy as gp
from gurobipy import GRB
import math




def find_utopia_obj3(char_per,t_s,del_t,Imax,Nv,Icmax,SOCdep,SOC_1,Cbat,SOC_xtra,weights):

    m3 = gp.Model('lin_prog3')
    m3.params.NonConvex = 2
    m3.reset(0)
    num_stab = 1000 # provide numerical stability by avoiding very small coefficients


    TT3 = []
    for v in range(0,Nv):
        TT3.append( max(math.floor((char_per[v] + t_s) / del_t) , 1)  ) # ceil to give atleast 1 timeslot of char_per < del_t

    max_TT3 = max(TT3) 

    # Decision variable declaration
    I3 = []
    for v in range(0,Nv):
        I3.append( m3.addVars((TT3[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )

    # lower and upper_bound battery power constraint
    bat_pwr_constr_l3 = []
    bat_pwr_constr_u3 = []
    for v in range(0,Nv):
        for i in range(0,TT3[v]): 
            bat_pwr_constr_l3.append( m3.addConstr( I3[v][i] >= 0 ) )
            bat_pwr_constr_u3.append( m3.addConstr( I3[v][i] <= Imax ) )

    # slot power constraint
    for i in range(0,max_TT3):
        slot_pwr3 = []
        for v in range(0,Nv):
            if i < TT3[v]:
                slot_pwr3.append(I3[v][i])
        
        m3.addConstr( sum(slot_pwr3) <= Icmax )

    # lower_bound and upper_bound Energy constraint
    tot_char_curr3 = []
    for v in range(0,Nv):
        each_veh_curr3 = []
        for i in range(0,TT3[v]):
            each_veh_curr3.append(I3[v][i])
            tot_char_curr3.append(I3[v][i])
        if(TT3[v] > 0):
            m3.addConstr( ( sum(each_veh_curr3) )* del_t  >= (SOCdep[v] - SOC_1[v])*Cbat[v] )
            m3.addConstr( ( sum(each_veh_curr3) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )

  
    m3.setObjective(-1*num_stab*(sum([a*b for a,b in zip(tot_char_curr3,weights)])), GRB.MINIMIZE)
    m3.update()
    m3.optimize()
    obj3 = m3.getObjective()
    utopia_obj3 = obj3.getValue() # utopia point 
    print(utopia_obj3)

    utopia_sol3 = {} # Decision variable, solution at utopia point 
    for v in range(0,Nv):
        for i in range(0,TT3[v]):
            utopia_sol3[v,i] = I3[v][i].x


    return TT3,utopia_obj3, utopia_sol3