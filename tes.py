
import gurobipy as gp
from gurobipy import GRB
import math
import sys

m = gp.Model('moo')
m.params.NonConvex = 2

#m.params.Presolve = 0
m.reset(clearall=0)






x = m.addVars((2), vtype=GRB.CONTINUOUS, lb=-10, ub=10) 



for i in range(2):
    m.addConstr( x[i] <= 5  )
    m.addConstr( x[i] >= -4  )




m.ModelSense = GRB.MINIMIZE

w1 = 0.5
w2 = 0.5
m.setObjective(  w1*( x[0]**2 + x[1]**2) + w2*(x[0]**2 + x[1]**2 - 2*x[0])  , GRB.MINIMIZE )



m.update()
m.optimize()
print(x[0].x)
print(x[1].x)
obj1 = m.getObjective()
print(obj1)

print(x[0].x)
print(x[1].x)




