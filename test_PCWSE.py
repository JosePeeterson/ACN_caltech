
import gurobipy as gp
from gurobipy import GRB
import math  
import datetime

m = gp.Model('moo')
m.params.NonConvex = 2

# m.params.Presolve = 0
m.reset(0)




#####   Paramters of calendric degradation     #####
p1 =   5.387*10**-5
p2 =   2.143*10**-5
adj_var = 1 # adjustment variable to push the charging to later

#####   Paramters of degradation due to current    #####
q1 =  -0.0001528
q2 =   0.0002643
q3 =   1.134e-05

#####   Paramters of cyclic degradation, piecewise  objectives   #####
p00b1 = 3.205*10**-6    
p10b1 = -0.0001132
p01b1 = 1.64*10**-6
p11b1 = 2.936*10**-6
p02b1 = -5.472*10**-9

p00b2 = 6.492*10**-6    
p10b2 = -6.808*10**-5   
p01b2 = 1.51*10**-6
p11b2 = 2.085*10**-6
p02b2 = -4.12*10**-9

p00b3 = 7.411*10**-6    
p10b3 = -2.378*10**-5   
p01b3 = 1.389*10**-6
p11b3 = 1.219*10**-6
p02b3 = -2.075*10**-9

p00b4 = 5.763*10**-6    
p10b4 = 1.011*10**-5   
p01b4 = 1.291*10**-6
p11b4 = 3.931*10**-7
p02b4 = 1.206*10**-9

p00b5 = 1.641*10**-6    
p10b5 = -1.809*10**-6   
p01b5 = 1.563*10**-6
p11b5 = 2.6*10**-7
p02b5 = 8.479*10**-10






# SOC_avg = [[1]]
# I = [[120]]

eps = 0.001
M = 120 + eps

del_t = 0.1


SOCdep = [0.19, 0, 0, 0, 0.19, 0, 0, 0, 0, 0, 0, 0, 0, 0]
SOC_1 = [0.1, 0, 0, 0, 0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
char_per = [2.433333333333333, 0, 0, 0, 10.149999999999908, 0, 0, 0, 0, 0, 0, 0, 0, 0]

##################    TESTINF FOR WORST CASE TIME TO SOLVE    #####################
SOCdep =   [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]#, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
SOC_1 =    [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]#, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
char_per = [4,  4,  4,  4,  4,  4,  4]#,  10,  10,  10,  10,  10,  10,  10 ]
##################    TESTINF FOR WORST CASE TIME TO SOLVE    #####################

start_time = datetime.datetime.now()

# SOCdep = [0.19, 0.19]
# SOC_1 = [0.1, 0.1]
# char_per = [2.433333333333333,10.149999999999908]

SOC_xtra = 0.001
t_s = 0

Nv = len(SOCdep)

Cbat = [570]*Nv

TT = []
for v in range(0,Nv):
    TT.append( math.ceil((char_per[v] + t_s) / del_t) )

max_TT = max(TT)
Imax = 120

Icmax = Imax*Nv

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



b1 = []
b2 = []
b3 = []
b4 = []
b5 = []

for v in range(0,Nv):
    # b1.append( m.addVars((TT[v]),vtype=GRB.BINARY) )
    # b2.append( m.addVars((TT[v]),vtype=GRB.BINARY) )
    b3.append( m.addVars((TT[v]),vtype=GRB.BINARY) )
    b4.append( m.addVars((TT[v]),vtype=GRB.BINARY) )
    b5.append( m.addVars((TT[v]),vtype=GRB.BINARY) )


        
# b1  = m.addVar(vtype=GRB.BINARY, name="b1")
# b2  = m.addVar(vtype=GRB.BINARY, name="b2")
# b3  = m.addVar(vtype=GRB.BINARY, name="b3")
# b4  = m.addVar(vtype=GRB.BINARY, name="b4")
# b5  = m.addVar(vtype=GRB.BINARY, name="b5")


cap_loss = []
for v in range(0,Nv):
    cap_loss.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=0.05) )
for v in range(0,Nv):
    for i in range(0,TT[v]):

        # b1  = m.addVar(vtype=GRB.BINARY)
        # b2  = m.addVar(vtype=GRB.BINARY)
        # b3  = m.addVar(vtype=GRB.BINARY)
        # b4  = m.addVar(vtype=GRB.BINARY)
        # b5  = m.addVar(vtype=GRB.BINARY)

        obj1 = m.addVar(vtype=GRB.CONTINUOUS, name="obj1")
        obj2 = m.addVar(vtype=GRB.CONTINUOUS, name="obj2")
        obj3 = m.addVar(vtype=GRB.CONTINUOUS, name="obj3")
        obj4 = m.addVar(vtype=GRB.CONTINUOUS, name="obj4")
        obj5 = m.addVar(vtype=GRB.CONTINUOUS, name="obj5")


        m.addConstr( obj5, GRB.EQUAL, p00b1 + p10b1*SOC_avg[v][i] + p01b1*(I[v][i]) + p11b1*SOC_avg[v][i]*(I[v][i]) + p02b1*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )# + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3 )
        m.addConstr( obj4,GRB.EQUAL, p00b2 + p10b2*SOC_avg[v][i] + p01b2*(I[v][i]) + p11b2*SOC_avg[v][i]*(I[v][i]) + p02b2*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)
        m.addConstr( obj3,GRB.EQUAL, p00b3 + p10b3*SOC_avg[v][i] + p01b3*(I[v][i]) + p11b3*SOC_avg[v][i]*(I[v][i]) + p02b3*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)
        # m.addConstr(obj2, GRB.EQUAL, p00b4 + p10b4*SOC_avg[v][i] + p01b4*(I[v][i]) + p11b4*SOC_avg[v][i]*(I[v][i]) + p02b4*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)
        # m.addConstr(obj1, GRB.EQUAL, p00b5 + p10b5*SOC_avg[v][i] + p01b5*(I[v][i]) + p11b5*SOC_avg[v][i]*(I[v][i]) + p02b5*(I[v][i])**2  + p1*SOC_avg[v][i]*adj_var + p2 )#  + q1*(I[v][i]/Cbat[v])**2 + q2*(I[v][i]/Cbat[v]) + q3)

        #m.addConstr(x, GRB.EQUAL, b1 + b2 + b3 + b4 + b5 )
        m.addConstr( b3[v][i] + b4[v][i] + b5[v][i], GRB.EQUAL, 1 ) # b1[v][i] + b2[v][i] + b3[v][i] + b3[v][i] +
        #m.addConstr( b1 + b2 + b3 + b4 + b5 , GRB.EQUAL, 1 ) #b1 + b2 + b3 + b4 + b5
        # # # Model if x>y then b1 = 1, otherwise b1 = 0

        # m.addGenConstrIndicator(b1[v][i], True, I[v][i] <= 120*SOC_avg[v][i])
        # m.addGenConstrIndicator(b2[v][i], True, I[v][i] >= 120*SOC_avg[v][i])
        # m.addGenConstrIndicator(b2[v][i], True, I[v][i] <= 240*SOC_avg[v][i])
        # m.addGenConstrIndicator(b3[v][i], True, I[v][i] >= 240*SOC_avg[v][i])
        m.addGenConstrIndicator(b3[v][i], True, I[v][i] <= 480*SOC_avg[v][i])
        m.addGenConstrIndicator(b4[v][i], True, I[v][i] >= 480*SOC_avg[v][i])
        m.addGenConstrIndicator(b4[v][i], True, I[v][i] <= 960*SOC_avg[v][i])
        m.addGenConstrIndicator(b5[v][i], True, I[v][i] >= 960*SOC_avg[v][i])

        # m.addGenConstrIndicator(b1, True, I[v][i] <= 120*SOC_avg[v][i])
        # m.addGenConstrIndicator(b2, True, I[v][i] >= 120*SOC_avg[v][i])
        # m.addGenConstrIndicator(b2, True, I[v][i] <= 240*SOC_avg[v][i])
        # m.addGenConstrIndicator(b3, True, I[v][i] >= 240*SOC_avg[v][i])
        # m.addGenConstrIndicator(b3, True, I[v][i] <= 480*SOC_avg[v][i])
        # m.addGenConstrIndicator(b4, True, I[v][i] >= 480*SOC_avg[v][i])
        # m.addGenConstrIndicator(b4, True, I[v][i] <= 960*SOC_avg[v][i])
        # m.addGenConstrIndicator(b5, True, I[v][i] >= 960*SOC_avg[v][i])

        

        m.addConstr((b5[v][i] == 1) >> (cap_loss[v][i] ==  obj5), name="indicator_constr1")
        m.addConstr((b4[v][i] == 1) >> (cap_loss[v][i] ==   obj4  ), name="indicator_constr2")
        m.addConstr((b3[v][i] == 1) >> (cap_loss[v][i] ==  obj3  ), name="indicator_constr3")
        # m.addConstr((b2[v][i] == 1) >> (cap_loss[v][i] ==  obj2  ), name="indicator_constr4")
        # m.addConstr((b1[v][i] == 1) >> (cap_loss[v][i] ==  obj1  ), name="indicator_constr5")

        # m.addConstr((b5 == 1) >> (cap_loss[v][i] ==  obj5), name="indicator_constr1")
        # m.addConstr((b4 == 1) >> (cap_loss[v][i] ==   obj4  ), name="indicator_constr2")
        # m.addConstr((b3 == 1) >> (cap_loss[v][i] ==  obj3  ), name="indicator_constr3")
        # m.addConstr((b2 == 1) >> (cap_loss[v][i] ==  obj2  ), name="indicator_constr4")
        # m.addConstr((b1 == 1) >> (cap_loss[v][i] ==  obj1  ), name="indicator_constr5")
        


cap_loss_array = []
for v in range(0,Nv):
    for i in range(0,TT[v]):
        cap_loss_array.append(cap_loss[v][i])

m.setObjective( sum( cap_loss_array),GRB.MINIMIZE)


m.update()

m.optimize()



for v in range(0,Nv):
    for i in range(0,TT[v]):
        print(I[v][i].x)
        print(SOC_avg[v][i].x)
        #print(b1.x,b2.x,b3.x,b4.x,b5.x)
        print(b3[v][i].x,b4[v][i].x,b5[v][i].x) #b1[v][i].x,b2[v][i].x,b3[v][i].x,
        print(I[v][i].x , 120*SOC_avg[v][i].x)
        print(I[v][i].x , 240*SOC_avg[v][i].x)
        print(I[v][i].x , 480*SOC_avg[v][i].x)
        print(I[v][i].x , 960*SOC_avg[v][i].x)

print('\ntime elapsed = ', datetime.datetime.now() - start_time )




# # get the set of variables
# x = m.getVars()
# print(x)
# # Ensure status is optimal
# assert m.Status == GRB.Status.OPTIMAL
# # Query number of multiple objectives , and number of solutions
# # nSolutions = m.SolCount
# # nObjectives = m.NumObj
# # print ('Problem has ' , nObjectives , ' objectives')
# # print ('Gurobi found ', nSolutions , ' solutions ')
# # # For each solution , print value of first three variables , and
# # # value for each objective function
# # solutions = []
# # for s in range( nSolutions ):
# #     # Set which solution we will query from now on
# #     m.params.SolutionNumber = s
# #     # Print objective value of this solution in each objective
# #     print('Solution ' , s,':','\n')
# #     for o in range( nObjectives ):
# #         # Set which objective we will query
# #         m.params.ObjNumber = o
# #         # Query the o-th objective value
# #         print('\n','objective value = ',m.ObjNVal , '\n')
# #     # print first three variables in the solution
# #     for j in len(x):
# #         print(x[j]. VarName , x[j].Xn , end='')
# #     print('')

# # # query the full vector of the o-th solution
# # solutions.append(m.getAttr('Xn',x))

