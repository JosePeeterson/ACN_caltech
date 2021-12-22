import gurobipy as gp
from gurobipy import GRB
import math
from numpy import datetime_as_string
import pandas as pd
import sys
import datetime
import dateutil

def cost_optimization(Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time,vbat):
    
    begin_time = dateutil.parser.parse(begin_time)

    df = pd.read_csv('20210501-20210508 CAISO Average Price.csv')

    #print(len(df))
    # print(int(df['date'][2296][-5:-3]))
    # print(int(df['date'][2296][-2:]))
    # date = df['date'][2296][0:8]
    # print(date)
    # format_str = '%m/%d/%Y' # The format
    # datetime_obj = datetime.datetime.strptime(date, format_str)
    # print(str(datetime_obj.date()))

    Minute_Elec_price = {}

    i = 0
    j=0
    while(i < len(df)):
        date = str(df['date'][i][0:8])
        hr = str(df['date'][i][-5:-3])
        min = int(df['date'][i][-2:])
        min = min + j
        min = str(min)
        price = df['price ($/MWh)'][i]

        format_str = '%m/%d/%Y %H:%M' # The format
        full_date = date + " " + hr + ":" + min
        datetime_obj = datetime.datetime.strptime(full_date, format_str)
        #print(datetime_obj)
        Minute_Elec_price[datetime_obj] = abs(price)/1000 # Mwh -> Kwh

        j+=1
        if (j == 5):
            i+=1
            j=0
        

    #print(Minute_Elec_price.values())
    #sys.exit()
 


    # Nv = 3
    # Tdep = [10,4,8]
    # del_t = 2
    t_s = 0


    Imax = 80
    Icmax = Nv*80


    # Cbat = 20
    # Ebat = 300
    # SOCdep = [0.8, 0.6, 0.7]
    # SOC_1 = [0.1, 0.2, 0.1]
    SOC_xtra = 0.001




    TT = []
    for v in range(0,Nv):
        TT.append( math.ceil((char_per[v] + t_s) / del_t) )

    max_TT = max(TT) 

    


    WEPV = []
    viz_WEPV = {v:[] for v in range(0,Nv)}
    viz_timev = {v:[] for v in range(0,Nv)}
    #print(curr_time)
    for v in range(0,Nv):
        curr_time = begin_time
        for i in range(0,TT[v]): 
            #print(curr_time)
            WEPV.append( Minute_Elec_price[curr_time] )
            viz_WEPV[v].append( Minute_Elec_price[curr_time] )
            viz_timev[v].append( curr_time )
            curr_time = curr_time + datetime.timedelta(minutes=6)





    m = gp.Model('lin_prog')

    m.params.Presolve = 0
    m.reset(0)

    # Decision variables
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

    # upper_bound Energy constraint
    for v in range(0,Nv):
        each_veh_curr = []
        for i in range(0,TT[v]):
            each_veh_curr.append(I[v][i])
        if(TT[v] > 0):
            m.addConstr( ( sum(each_veh_curr) )* del_t  <= (SOCdep[v] - SOC_1[v] + SOC_xtra)*Cbat[v]  )

    max_timeslot = 307
    max_current = 100
    max_char_cost = 98.37*max_timeslot*Nv*vbat*max_current*del_t


    # Charging cost Objective #1
    m.setObjective((1/max_char_cost)*sum([a*b for a,b in zip(tot_char_curr,WEPV)]), GRB.MINIMIZE)

    m.update()
    m.optimize()

    print('\n')

    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i].x
            #I_temp.append([v,i,I[v][i].x])

    print(I_temp)
    status = m.Status
    if status in (GRB. INF_OR_UNBD , GRB. INFEASIBLE , GRB. UNBOUNDED ):
        print("The model cannot be solved because it is infeasible or unbounded ")
        sys.exit(1)
    if status != GRB.OPTIMAL:
        print ("Optimization was stopped with status" + str( status ))
        sys.exit(1)

    return TT, I_temp,viz_WEPV, viz_timev

    