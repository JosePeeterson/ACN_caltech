#from MOO_apprx_bat_deg import MOO_bat_deg_obj
import winsound
from MOO_PceWise_apprx_bat_deg import MOO_bat_deg_obj
from MOO_rental_avail import MOO_rental_avail_obj
from MOO_char_cost import MOO_char_cost_obj
from find_utopia_obj1 import find_utopia_obj1
from find_utopia_obj2 import find_utopia_obj2
from find_utopia_obj3 import find_utopia_obj3
from evaluate_nadir_pnts import evaluate_nadir_pnts
from two_obj_nadir import two_obj_nadir 
import gurobipy as gp
from gurobipy import GRB
import math
import sys

def mult_obj_opt(SOC_xtra,Imax,max_timeslot,df,Weight,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time,vbat):

    m = gp.Model('moo')
    m.params.NonConvex = 2

    #m.params.Presolve = 0
    m.reset(0)

    Icmax = Nv*Imax

    t_s = 0 # account for time for optimization

    TT = []
    for v in range(0,Nv):
        TT.append( max(math.floor((char_per[v] + t_s) / del_t) , 1)  ) # ceil to give atleast 1 timeslot of char_per < del_t

    max_TT = max(TT) 

    # Decision variable declaration
    I = []
    for v in range(0,Nv):
        I.append( m.addVars((TT[v]), vtype=GRB.CONTINUOUS, lb=0, ub=Imax) )

    num_stab = 10000 # provide numerical stability by avoiding very small coefficients

    
    W1 = Weight[0]
    W2 = Weight[1]
    W3 = Weight[2]

    SOCdep_n = SOCdep
    char_per_n = char_per
    SOC_1_n = SOC_1


    WEPV,viz_WEPV, viz_timev_cost  = MOO_char_cost_obj(SOC_xtra,df,m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time)

    cap_loss_array,viz_timev_bat,cap_loss  = MOO_bat_deg_obj(SOC_xtra,m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time)

    tot_char_curr, weights = MOO_rental_avail_obj(SOC_xtra,m,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat)

    TT1,utopia_obj1, utopia_sol1 = find_utopia_obj1(num_stab,WEPV,Nv,Imax,del_t,t_s,Icmax,SOCdep_n, char_per_n, SOC_1_n, SOC_xtra,Cbat)
    #TT2,utopia_obj2, utopia_I_sol2, utopia_SOC_avg_sol2 = find_utopia_obj2(num_stab,char_per_n,t_s,del_t,Imax,Nv,Icmax,SOCdep_n,SOC_1_n,Cbat,SOC_xtra)
    TT3,utopia_obj3, utopia_sol3 = find_utopia_obj3(num_stab,char_per_n,t_s,del_t,Imax,Nv,Icmax,SOCdep_n,SOC_1_n,Cbat,SOC_xtra,weights)
    #nadir_obj1,nadir_obj2,nadir_obj3 = evaluate_nadir_pnts(Cbat,del_t,SOC_1_n,TT1,TT2,TT3,Nv,utopia_sol1,utopia_sol3,weights,WEPV,num_stab,utopia_I_sol2, utopia_SOC_avg_sol2)
    TT2 = 1
    utopia_I_sol2 = 1
    utopia_SOC_avg_sol2 = 1
    nadir_obj1,nadir_obj3 = two_obj_nadir(Cbat,del_t,SOC_1_n,TT1,TT2,TT3,Nv,utopia_sol1,utopia_sol3,weights,WEPV,num_stab,utopia_I_sol2, utopia_SOC_avg_sol2)
    #print(nadir_obj1,nadir_obj2,nadir_obj3)

 
                    # m.ModelSense = GRB.MINIMIZE

    # use minimum weight of 10,000 for outright domination to be noticeable
    #print('\n',utopia_obj1, nadir_obj1, utopia_obj2, nadir_obj2,'\n') #- utopia_obj1- utopia_obj2
                    # m.setObjectiveN( 1*( ( sum([num_stab*a*b*vbat for a,b in zip(tot_char_curr,WEPV)]) - utopia_obj1 ) / ( nadir_obj1 - utopia_obj1 ) ) ,0,weight = 1)
                    # m.setObjectiveN( 1*( ( sum( [num_stab*c for c in cap_loss_array]) - utopia_obj2 ) / (nadir_obj2 - utopia_obj2 ) ) ,1,weight = 1)
                    # #m.setObjectiveN( ( num_stab*(sum([a*b for a,b in zip(tot_char_curr,weights)]) ) - utopia_obj3 ) / (nadir_obj3 - utopia_obj3) ,2,weight = W3 )

    div_obj1 = 1/( nadir_obj1 - utopia_obj1 )
    div_obj3 = 1/( nadir_obj3 - utopia_obj3 )

    m.setObjective( W1*(  sum([num_stab*a*b for a,b in zip(tot_char_curr,WEPV)])  - utopia_obj1 )*div_obj1 +  W2*(   -1*num_stab*(sum([a*b for a,b in zip(tot_char_curr,weights)])) - utopia_obj3 )*div_obj3    , GRB.MINIMIZE )
    
    #+  W2*( )*div_obj3

    m.update()
    print('\n Weights =', W1, W2, W3, '\n')
    m.optimize()
    
    if (m.Status == GRB.Status.INFEASIBLE):
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)
        m.computeIIS()
        m.write("model.ilp")

    tot_char_curr_VAL = []
    cap_loss_array_VAL = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            tot_char_curr_VAL.append(I[v][i].x)
            cap_loss_array_VAL.append(cap_loss[v][i].x)

    ob1 = (  sum([num_stab*a*b for a,b in zip(tot_char_curr_VAL,WEPV)])  )  # - utopia_obj1 *div_obj1
    ob3 = ( -1*num_stab*(sum([a*b for a,b in zip(tot_char_curr_VAL,weights)])) ) # - utopia_obj2  *div_obj2
                    # obj1 = m.getObjective(0)
                    # ob1 = obj1.getValue()
                    # obj2 = m.getObjective(1)
                    # ob2 = obj2.getValue()
                    # obj3 = m.getObjective(2)
    ob2 = 1

    print('\n')
    # ####################  CHECK SOLUTION AND OBJECTIVE FUNC. VALUES    ##########################
    # print('\n' , 'my obj vals' , ob1, ob2, ob3)
    # print('\n')

    # # get the set of variables
    # x = m. getVars()
    # # Ensure status is optimal
    # assert m.Status == GRB.Status.OPTIMAL
    # # Query number of multiple objectives , and number of solutions
    # nSolutions = m.SolCount
    # nObjectives = m.NumObj
    # print ('Problem has ' , nObjectives , ' objectives')
    # print ('Gurobi found ', nSolutions , ' solutions ')
    # # For each solution , print value of first three variables , and
    # # value for each objective function
    # solutions = []
    # for s in range( nSolutions ):
    #     # Set which solution we will query from now on
    #     m.params.SolutionNumber = s
    #     # Print objective value of this solution in each objective
    #     print('Solution ' , s,':','\n')
    #     for o in range( nObjectives ):
    #         # Set which objective we will query
    #         m.params.ObjNumber = o
    #         # Query the o-th objective value
    #         print('\n','objective value = ',m.ObjNVal , '\n')
    #     # # print first three variables in the solution
    #     # n = min(x)
    #     # for j in range(n):
    #     #     print(x[j]. VarName , x[j].Xn , end='')
    #     # print('')

    # # query the full vector of the o-th solution
    # solutions.append(m.getAttr('Xn',x))
    # ##############################################################################################


    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i].x
            #I_temp.append([v,i,I[v][i].x])

    # Status checking
    status = m.Status
    if status in (GRB. INF_OR_UNBD , GRB. INFEASIBLE , GRB. UNBOUNDED ):
        print("The model cannot be solved because it is infeasible or unbounded ")
        sys. exit (1)
    if status != GRB.OPTIMAL:
        print ("Optimization was stopped with status" + str( status ))
        sys. exit (1)



    return TT, I_temp, viz_timev_bat, viz_WEPV, viz_timev_cost, ob1, ob2, ob3,max_TT, utopia_obj1, nadir_obj1, utopia_obj3, nadir_obj3








































