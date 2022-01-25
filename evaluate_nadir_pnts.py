def evaluate_nadir_pnts(Cbat,del_t,SOC_1,TT1,TT2,TT3,Nv,utopia_sol1,utopia_sol3,weights,WEPV,num_stab,utopia_I_sol2, utopia_SOC_avg_sol2, rec_b4, rec_b5, rec_coef_5, rec_coef_4):

    #####   Paramters of cyclic degradation, SINGLE piece objective   #####
    p00b1 = 1.099*10**-5    
    p10b1 = -1.962*10**-5
    p01b1 = 1.268*10**-6
    p11b1 = 9.204*10**-7
    p02b1 = -1.159*10**-9

    #####   Paramters of calendric degradation, piecewise  objectives   #####
    adj_var = 2 # adjustment variable to push the charging to later
    p1 = 0.0001347
    p2 = 5.356*10**-5

    all_utopia_pnts = [utopia_sol1,utopia_I_sol2,utopia_sol3]
    obj1_list = [] # posible nadir components from different utopia sols.
    obj2_list = [] # posible nadir components from different utopia sols.
    obj3_list = [] # posible nadir components from different utopia sols.

    utopia_SOC_sol1 = {}
    utopia_SOC_avg_sol1 = {}
    # compute SOC_avg array for utopia_sol1 and utopia_sol1
    print('\n')
    print(TT1,TT2,TT3)
    print('\n')
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT1[v]):
            if first == 1:
                utopia_SOC_sol1[v,i] = SOC_1[v] + (utopia_sol1[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol1[v,i] = SOC_1[v] + (0.5*(utopia_sol1[v,i]* del_t)) / Cbat[v]
                first = 0
            else:
                utopia_SOC_sol1[v,i] = utopia_SOC_sol1[v,i-1] + (utopia_sol1[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol1[v,i] = utopia_SOC_sol1[v,i-1] + (0.5*(utopia_sol1[v,i]* del_t)) / Cbat[v]
                

    utopia_sol2 = utopia_I_sol2
    utopia_SOC_sol2 = {}
    utopia_SOC_avg_sol2 = {}
    # compute SOC_avg array for utopia_sol1 and utopia_sol1
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT2[v]):
            if first == 1:
                utopia_SOC_sol2[v,i] = SOC_1[v] + (utopia_sol2[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol2[v,i] = SOC_1[v] + (0.5*(utopia_sol2[v,i]* del_t)) / Cbat[v]
                first = 0
            else:
                utopia_SOC_sol2[v,i] = utopia_SOC_sol2[v,i-1] + (utopia_sol2[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol2[v,i] = utopia_SOC_sol2[v,i-1] + (0.5*(utopia_sol2[v,i]* del_t)) / Cbat[v]

    utopia_SOC_sol3 = {}
    utopia_SOC_avg_sol3 = {}
    # compute SOC_avg array for utopia_sol1 and utopia_sol1
    for v in range(0,Nv):
        first = 1
        for i in range(0,TT3[v]):
            if first == 1:
                utopia_SOC_sol3[v,i] = SOC_1[v] + (utopia_sol3[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol3[v,i] = SOC_1[v] + (0.5*(utopia_sol3[v,i]* del_t)) / Cbat[v]
                first = 0
            else:
                utopia_SOC_sol3[v,i] = utopia_SOC_sol3[v,i-1] + (utopia_sol3[v,i]* del_t) / Cbat[v]
                utopia_SOC_avg_sol3[v,i] = utopia_SOC_sol3[v,i-1] + (0.5*(utopia_sol3[v,i]* del_t)) / Cbat[v]


    utopia_SOC_avg = [utopia_SOC_avg_sol1, utopia_SOC_avg_sol2,utopia_SOC_avg_sol3]

    for utop_pnt,utop_soc_avg in zip(all_utopia_pnts,utopia_SOC_avg):

        Tot_obj_2 = 0
        for v in range(0,Nv):
            for i in range(0,TT2[v]):
                obj_2 = p00b1 + p10b1*utop_soc_avg[v,i] + p01b1*(utop_pnt[v,i]) + p11b1*utop_soc_avg[v,i]*(utop_pnt[v,i]) + p02b1*(utop_pnt[v,i])**2  + p1*utop_soc_avg[v,i]*adj_var + p2
                Tot_obj_2 += num_stab*obj_2
        
        obj2_list.append( Tot_obj_2)

        tot_char_curr = []
        for v in range(0,Nv):
            for i in range(0,TT2[v]):
                tot_char_curr.append(utop_pnt[v,i])
        # 1st objective
        print(tot_char_curr,WEPV)
        obj1_list.append( num_stab*sum([a*b for a,b in zip(tot_char_curr,WEPV)])  )
        # 3rd objective
        obj3_list.append( -1*num_stab*(sum([a*b for a,b in zip(tot_char_curr,weights)])) )
    
    nadir_obj1 = max(obj1_list)
    nadir_obj2 = max(obj2_list)
    nadir_obj3 = max(obj3_list)

   
    return nadir_obj1,nadir_obj2,nadir_obj3


