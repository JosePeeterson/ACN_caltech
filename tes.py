import gurobipy as gp
from gurobipy import GRB
import math
import sys
import datetime
import dateutil


Nv = 5

SOCdep = [0.36,0,0,0,0]

char_per = [8,0,0,0,0]
SOC_1 = [0.1,0,0,0,0]
del_t = 0.1
Cbat = [270]*5


t_s = 0

Imax = 100
Icmax = Nv*Imax

SOC_xtra = 0.01
soc_min = 0 
soc_max = 1

Tiv = 30 # temperature

ks1 = -4.092*(10**-4)
ks2 = -2.167 
ks3 = 1.408*(10**-5)
ks4 = 6.130

I_lim = 1


TT = []
for v in range(0,Nv):
    TT.append( math.ceil((char_per[v] + t_s) / del_t) )

max_TT = max(TT) 


m = gp.Model('bat_deg')
m.params.NonConvex = 2

m.params.Presolve = 0
m.reset(0)
# Decision variable declaration
I = []
for v in range(0,Nv):
    I.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb= 0, ub=Imax) )


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














Ah_log = []
for v in range(0,Nv):
    Ah_log.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS,lb= -10000, ub=1000) )

temp_ah = []
for v in range(0,Nv):
    temp_ah.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb= 0, ub=del_t*Imax) )

exp_ah = []
for v in range(0,Nv):
    exp_ah.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb= 1, ub=22027) )


for v in range(0,Nv):
    for i in range(0,TT[v]):
        m.addConstr(temp_ah[v][i], GRB.EQUAL, (I[v][i]*del_t) + I_lim )
        m.addGenConstrExp(temp_ah[v][i], exp_ah[v][i])
        m.addGenConstrLog(temp_ah[v][i], Ah_log[v][i])
        

Ah_array = []
nat_log_array = []



for v in range(0,Nv):
    for i in range(0,TT[v]):
        Ah_array.append(Ah_log[v][i])


m.setObjective( 1 , GRB.MINIMIZE)
#m.setObjective( sum(B_array + Ah_array + Crate_array + b1_array + SOC_array + d_array + a1_a2_array), GRB.MINIMIZE)

m.update()
m.optimize()

#m.printQuality()

print('\n')

I_temp = {}

for v in range(0,Nv):
    for i in range(0,TT[v]):
        # print(temp_ah[v][i].x)
        # print((Ah_log[v][i]).x)
        # print(math.log(temp_ah[v][i].x) )
        print(math.exp(temp_ah[v][i].x) )
        print(exp_ah[v][i].x)










'''
m = gp.Model('test')
m.params.NonConvex = 2

m.params.Presolve = 0
m.reset(0)

Ah_log = []
for v in range(2):
    Ah_log.append( m.addVars(3, vtype=GRB.CONTINUOUS) )

temp_ah = []
for v in range(0,2):
    temp_ah.append( m.addVars(3, vtype=GRB.CONTINUOUS, lb = 2) )


for v in range(0,2):
    for i in range(0,1):
        m.addGenConstrLog(temp_ah[v][i], Ah_log[v][i])

m.setObjective(  Ah_log[0][0] + Ah_log[1][0] + 10 , GRB.MINIMIZE)
#m.setObjective( sum(B_array + Ah_array + Crate_array + b1_array + SOC_array + d_array + a1_a2_array), GRB.MINIMIZE)

m.update()
m.optimize()


#m.printQuality()

print('\n')


for v in range(0,2):
    for i in range(0,1):
        print(temp_ah[v][i].x)
        print(Ah_log[v][i].x)

'''



