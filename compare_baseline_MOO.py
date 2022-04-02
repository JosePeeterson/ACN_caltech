import json
from re import X
import matplotlib.pyplot as plt
import datetime

with open( 'baseline_obj_1_2.txt','r') as f:
    base_obj_vals = json.loads(f.read())

with open( 'MOO_obj_1_2.txt','r') as f:
    MOO_obj_vals = json.loads(f.read())


# print(base_obj_vals[1][0])


print(sum(base_obj_vals[0][0])/10000)
print(sum(base_obj_vals[1][0])/10000)
print('\n')
print(sum(MOO_obj_vals[0][0])/10000)
print(sum(MOO_obj_vals[1][0])/10000)
print('\n')
print("amortized battery cost",11623.5 *(sum(MOO_obj_vals[1][0])/10000/210))


Base_peak = [15, 15, 12, 12, 15, 15, 15, 15, 15, 15, 9, 9, 15, 15, 15, 29, 0, 15, 12, 15, 27, 14, 15, 4, 12, 26, 40, 11, 9, 24, 22, 15, 22, 21, 15, 15, 14, 15, 29, 11, 
15, 27, 44, 30, 12, 9, 0, 15, 12, 25, 0, 15, 15, 15, 12, 15, 29, 16, 12, 15, 13, 28, 14, 15, 13, 15, 15, 29, 12, 15, 14, 15, 15, 8, 22, 35, 49, 62, 9, 20, 0]

x_base = [datetime.datetime(2021, 5, 1, 15, 30), datetime.datetime(2021, 5, 1, 18, 4), datetime.datetime(2021, 5, 1, 19, 1), datetime.datetime(2021, 5, 1, 20, 2), datetime.datetime(2021, 5, 1, 20, 42), datetime.datetime(2021, 5, 1, 21, 56), datetime.datetime(2021, 5, 2, 1, 50), datetime.datetime(2021, 5, 2, 15, 38), datetime.datetime(2021, 5, 2, 17, 50), datetime.datetime(2021, 5, 2, 23, 16), datetime.datetime(2021, 5, 3, 1, 8), datetime.datetime(2021, 5, 3, 1, 9), datetime.datetime(2021, 5, 3, 15, 28), datetime.datetime(2021, 5, 3, 17, 55), datetime.datetime(2021, 5, 3, 21, 13), datetime.datetime(2021, 5, 3, 21, 17), datetime.datetime(2021, 5, 3, 21, 45), datetime.datetime(2021, 5, 3, 23, 29), datetime.datetime(2021, 5, 4, 0, 
3), datetime.datetime(2021, 5, 4, 1, 18), datetime.datetime(2021, 5, 4, 1, 55), datetime.datetime(2021, 
5, 4, 2, 10), datetime.datetime(2021, 5, 4, 15, 0), 
datetime.datetime(2021, 5, 4, 16, 19), datetime.datetime(2021, 5, 4, 17, 42), datetime.datetime(2021, 5, 4, 17, 49), datetime.datetime(2021, 5, 4, 17, 56), 
datetime.datetime(2021, 5, 4, 18, 45), datetime.datetime(2021, 5, 4, 19, 11), datetime.datetime(2021, 5, 4, 19, 20), datetime.datetime(2021, 5, 4, 20, 35), 
datetime.datetime(2021, 5, 4, 21, 18), datetime.datetime(2021, 5, 4, 21, 23), datetime.datetime(2021, 5, 4, 21, 36), datetime.datetime(2021, 5, 4, 21, 43), 
datetime.datetime(2021, 5, 4, 21, 44), datetime.datetime(2021, 5, 4, 21, 52), datetime.datetime(2021, 5, 5, 2, 22), datetime.datetime(2021, 5, 5, 2, 37), datetime.datetime(2021, 5, 5, 3, 11), datetime.datetime(2021, 5, 5, 14, 35), datetime.datetime(2021, 5, 5, 15, 9), datetime.datetime(2021, 5, 5, 15, 26), datetime.datetime(2021, 5, 5, 15, 34), datetime.datetime(2021, 5, 5, 18, 16), datetime.datetime(2021, 5, 5, 
18, 51), datetime.datetime(2021, 5, 5, 19, 2), datetime.datetime(2021, 5, 5, 19, 12), datetime.datetime(2021, 5, 5, 20, 48), datetime.datetime(2021, 5, 5, 21, 14), datetime.datetime(2021, 5, 5, 22, 54), datetime.datetime(2021, 5, 6, 0, 58), datetime.datetime(2021, 5, 6, 3, 51), datetime.datetime(2021, 5, 6, 5, 
19), datetime.datetime(2021, 5, 6, 6, 5), datetime.datetime(2021, 5, 6, 15, 9), datetime.datetime(2021, 
5, 6, 15, 25), datetime.datetime(2021, 5, 6, 15, 51), datetime.datetime(2021, 5, 6, 17, 10), datetime.datetime(2021, 5, 6, 18, 30), datetime.datetime(2021, 
5, 6, 18, 51), datetime.datetime(2021, 5, 6, 18, 53), datetime.datetime(2021, 5, 6, 19, 3), datetime.datetime(2021, 5, 6, 20, 15), datetime.datetime(2021, 5, 6, 20, 37), datetime.datetime(2021, 5, 6, 21, 52), datetime.datetime(2021, 5, 7, 1, 23), datetime.datetime(2021, 5, 7, 1, 41), datetime.datetime(2021, 5, 
7, 2, 5), datetime.datetime(2021, 5, 7, 2, 48), datetime.datetime(2021, 5, 7, 2, 58), datetime.datetime(2021, 5, 7, 4, 37), datetime.datetime(2021, 5, 7, 13, 34), datetime.datetime(2021, 5, 7, 15, 14), datetime.datetime(2021, 5, 7, 15, 24), datetime.datetime(2021, 5, 7, 15, 33), datetime.datetime(2021, 5, 7, 15, 38), datetime.datetime(2021, 5, 7, 15, 44), datetime.datetime(2021, 5, 7, 16, 54), datetime.datetime(2021, 5, 7, 17, 11), datetime.datetime(2021, 5, 7, 18, 19)]

MOO_peak = [5, 7, 2, 1, 14, 1, 6, 14, 9, 6, 4, 8, 3, 4, 4, 3, 8, 3, 9, 7, 1, 5, 14, 9, 3, 4, 2, 10, 14, 5, 5, 10, 11, 12, 13, 8, 13, 8, 7, 2, 1, 3, 7, 2, 6, 9, 11, 5, 
2, 0, 0, 1, 4, 5, 3, 1, 9, 7, 6, 6, 3, 4, 5, 1, 0, 5, 5, 11, 6, 9, 9, 10, 3, 8, 3, 15, 12, 5, 19, 1, 21, 24, 26, 39, 9, 22, 0]

x_moo = [datetime.datetime(2021, 5, 1, 15, 30), datetime.datetime(2021, 5, 1, 18, 4), datetime.datetime(2021, 5, 1, 19, 1), datetime.datetime(2021, 5, 1, 20, 2), datetime.datetime(2021, 5, 1, 20, 42), datetime.datetime(2021, 5, 1, 21, 32), datetime.datetime(2021, 5, 1, 21, 56), datetime.datetime(2021, 5, 2, 1, 50), datetime.datetime(2021, 5, 2, 15, 38), datetime.datetime(2021, 5, 2, 17, 50), datetime.datetime(2021, 5, 2, 23, 16), datetime.datetime(2021, 5, 3, 1, 8), datetime.datetime(2021, 5, 3, 1, 9), datetime.datetime(2021, 5, 3, 15, 28), datetime.datetime(2021, 5, 3, 17, 55), datetime.datetime(2021, 5, 3, 21, 13), datetime.datetime(2021, 5, 3, 21, 17), datetime.datetime(2021, 5, 3, 21, 45), datetime.datetime(2021, 5, 3, 23, 29), datetime.datetime(2021, 5, 4, 0, 3), datetime.datetime(2021, 5, 4, 0, 48), datetime.datetime(2021, 5, 4, 1, 18), datetime.datetime(2021, 5, 4, 1, 55), datetime.datetime(2021, 5, 4, 2, 10), datetime.datetime(2021, 5, 4, 15, 0), datetime.datetime(2021, 5, 
4, 16, 19), datetime.datetime(2021, 5, 4, 17, 42), datetime.datetime(2021, 5, 4, 17, 49), datetime.datetime(2021, 5, 4, 17, 56), datetime.datetime(2021, 5, 
4, 18, 45), datetime.datetime(2021, 5, 4, 19, 11), datetime.datetime(2021, 5, 4, 19, 20), datetime.datetime(2021, 5, 4, 20, 35), datetime.datetime(2021, 5, 
4, 21, 18), datetime.datetime(2021, 5, 4, 21, 23), datetime.datetime(2021, 5, 4, 21, 36), datetime.datetime(2021, 5, 4, 21, 43), datetime.datetime(2021, 5, 
4, 21, 44), datetime.datetime(2021, 5, 4, 21, 52), datetime.datetime(2021, 5, 4, 22, 30), datetime.datetime(2021, 5, 4, 23, 20), datetime.datetime(2021, 5, 
5, 2, 22), datetime.datetime(2021, 5, 5, 2, 37), datetime.datetime(2021, 5, 5, 3, 11), datetime.datetime(2021, 5, 5, 14, 35), datetime.datetime(2021, 5, 5, 
15, 9), datetime.datetime(2021, 5, 5, 15, 26), datetime.datetime(2021, 5, 5, 15, 34), datetime.datetime(2021, 5, 5, 18, 16), datetime.datetime(2021, 5, 5, 18, 51), datetime.datetime(2021, 5, 5, 19, 2), datetime.datetime(2021, 5, 5, 19, 12), datetime.datetime(2021, 5, 5, 20, 48), datetime.datetime(2021, 5, 5, 21, 14), datetime.datetime(2021, 5, 5, 22, 54), datetime.datetime(2021, 5, 5, 23, 56), datetime.datetime(2021, 5, 6, 0, 58), datetime.datetime(2021, 5, 6, 3, 
51), datetime.datetime(2021, 5, 6, 5, 19), datetime.datetime(2021, 5, 6, 6, 5), datetime.datetime(2021, 
5, 6, 15, 9), datetime.datetime(2021, 5, 6, 15, 25), datetime.datetime(2021, 5, 6, 15, 51), datetime.datetime(2021, 5, 6, 17, 10), datetime.datetime(2021, 5, 6, 18, 19), datetime.datetime(2021, 5, 6, 18, 30), datetime.datetime(2021, 5, 6, 18, 51), datetime.datetime(2021, 5, 6, 18, 53), datetime.datetime(2021, 5, 6, 19, 3), datetime.datetime(2021, 5, 6, 20, 15), 
datetime.datetime(2021, 5, 6, 20, 37), datetime.datetime(2021, 5, 6, 21, 52), datetime.datetime(2021, 5, 7, 1, 23), datetime.datetime(2021, 5, 7, 1, 41), datetime.datetime(2021, 5, 7, 2, 5), datetime.datetime(2021, 5, 7, 2, 48), datetime.datetime(2021, 5, 7, 2, 58), datetime.datetime(2021, 5, 7, 4, 37), datetime.datetime(2021, 5, 7, 13, 34), datetime.datetime(2021, 5, 7, 15, 14), datetime.datetime(2021, 5, 7, 15, 24), datetime.datetime(2021, 5, 7, 15, 33), datetime.datetime(2021, 5, 7, 15, 38), datetime.datetime(2021, 5, 7, 15, 44), datetime.datetime(2021, 5, 7, 16, 54), datetime.datetime(2021, 5, 7, 17, 11), datetime.datetime(2021, 5, 7, 18, 19)]

plt.plot(x_base,Base_peak,'r2'  )
plt.plot(x_moo,MOO_peak,'b2'  )
# multiple lines with varying ymin and ymax
plt.vlines(x=x_base, ymin=[0]*len(Base_peak), ymax=Base_peak, colors='red', ls='-', lw=1, label='Baseline')
# multiple lines with varying ymin and ymax
plt.vlines(x=x_moo, ymin=[0]*len(MOO_peak), ymax=MOO_peak, colors='blue', ls='-', lw=1, label='Proposed')
plt.xlabel('Optimization time / (date-Hr-Min)')
plt.ylabel('Total Peak power period at each optimization time / (# time slots)')
plt.legend()
#plt.xticks(rotation=90)
plt.show()

print(len(x_moo),len(x_base))


