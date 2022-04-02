#from MOO_apprx_bat_deg import MOO_bat_deg_obj
import winsound
from base_PceWise_apprx_bat_deg import base_bat_deg_obj
from base_rental_avail import base_rental_avail_obj
from base_char_cost import base_char_cost_obj
import math
import sys

def base_obj_opt(ts_width,soc_init,SOC_xtra,Imax,df,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time,vbat):


    Icmax = Nv*Imax

    t_s = 0 # account for time for optimization

    TT = []
    for v in range(0,Nv):
        # deadline_TT is the timeslots untill deadline is reached
        deadline_TT = 1 if (((char_per[v] + t_s) / del_t) > 0 and ((char_per[v] + t_s) / del_t ) < 1  ) else math.floor((char_per[v] + t_s) / del_t)
        # full_charge_TT is the timeslots untill vehicle is charged fully to 1.
        full_charge_TT = math.ceil( (max( 1 - soc_init[v],0)*Cbat[v]) / (Imax*del_t) )


        TT.append( min( full_charge_TT , deadline_TT )  ) # ceil to give atleast 1 timeslot of char_per < del_t

    print('\n\n\n')
    print(TT)
    print('\n\n\n')

    max_TT = max(TT) 

    # Decision variable declaration
    I = []
    for v in range(0,Nv):
        I.append([])
        for i in range(0,TT[v]):
            I[v].append(Imax)

    num_stab = 10000 # provide numerical stability by avoiding very small coefficients




    WEPV,viz_WEPV, viz_timev_cost  = base_char_cost_obj(vbat,ts_width,SOC_xtra,df,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat, begin_time)

    viz_timev_bat,cap_loss  = base_bat_deg_obj(ts_width,SOC_xtra,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat,begin_time)

    weights,peak_per_veh = base_rental_avail_obj(SOC_xtra,I,TT,max_TT,Imax,Icmax,Nv, SOCdep, char_per, SOC_1, del_t,Cbat)


    tot_char_curr_VAL = []
    cap_loss_array_VAL = []
    for v in range(0,Nv):
        for i in range(0,TT[v]):
            tot_char_curr_VAL.append(I[v][i])
            cap_loss_array_VAL.append(cap_loss[v][i])

    ob1 = (  sum([num_stab*a*b for a,b in zip(tot_char_curr_VAL,WEPV)])  )  # - utopia_obj1 *div_obj1
    ob2 = num_stab*sum( cap_loss_array_VAL)
    ob3 = ( -1*num_stab*(sum([a*b for a,b in zip(tot_char_curr_VAL,weights)])) ) # - utopia_obj2  *div_obj2


    print('\n')


    I_temp = {}

    for v in range(0,Nv):
        for i in range(0,TT[v]):
            I_temp[v,i] = I[v][i]
            #I_temp.append([v,i,I[v][i].x])

    return TT, I_temp, viz_timev_bat, viz_WEPV, viz_timev_cost, ob1, ob2, ob3,max_TT,peak_per_veh








































