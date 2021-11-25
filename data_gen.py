import secrets                              # imports secure module.
import pandas as pd
from matplotlib import colors
import json
import numpy as np
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime

available_power_modes = ['2','10','50']    # https://www.energy.gov/eere/electricvehicles/vehicle-charging ; 120kWh is Tesla's supercharger (optional)
kappa = [0.2,0.4,0.6]
initial_battery = [0.1, 0.2, 0.3, 0.4]
aggregators = [0, 1, 2, 3, 4]
data = json.load(open('acndata_sessions_2021.json'))
df = pd.DataFrame(data["_items"])
df = df[df.userInputs.notnull()]
df.reset_index(inplace=True)




num_users = len(df.index)
user_deadlines = []
user_demands = []
user_initial = []
user_power_modes = []
user_priorities = []
user_arrivals = []
user_arr_slots = []
user_agg_id = []

def _generate_arrival_time(starting_time = 9):
	std_dev = 0.5
	mean = starting_time
	dist = np.random.normal(mean, std_dev, num_users)
	user_arrivals = [round(round(elem *2) / 2, 1) for elem in dist ] # [round(elem, 1) for elem in dist ]
	# count, bins, ignored = plt.hist(user_arrivals, 30, density=True)
	# plt.plot(bins, 1/(std_dev * np.sqrt(2 * np.pi)) * np.exp( - (bins - mean)**2 / (2 * std_dev**2) ), linewidth=2, color='r')
	# plt.show()
        
		
		
def _get_energy_demand_deadline():
	for item in range(num_users):
		user_data = df.loc[item, 'userInputs']
		rounded_time = int(math.ceil(user_data[0]['minutesAvailable']/10.0)) * 10   #round(user_data[0]['minutesAvailable']/60, 1)
		user_deadlines.append(int(rounded_time / 10))     #round((rounded_time * 2) / 2)) #user_deadlines.append(rounded_time)
		demand = round(user_data[0]['kWhRequested'])
		demand = demand + 1 if (demand%2 == 1) else demand
		user_demands.append(int(demand))

	
def _generate_power_modes():
	secure_random = secrets.SystemRandom()
	list_of_power_modes = {1, 2, 3, 4}
	for item in range(num_users):
		random_item = secure_random.sample(list_of_power_modes, 1)[0]
		user_power_modes.append('.'.join(available_power_modes[:random_item]))
		
		
def _generate_agg_id():
	secure_random = secrets.SystemRandom()
	for item in range(num_users):
		random_item = secure_random.sample(aggregators, 1)[0]
		user_agg_id.append(random_item)
	
	
def _generate_kappa():
	secure_random = secrets.SystemRandom()
	for item in range(num_users):	
		user_priorities.append(secure_random.sample(kappa, 1)[0])
		
		
def _generate_initial_energy():
	secure_random = secrets.SystemRandom()
	for item in range(num_users):	
		battery_level = secure_random.sample(initial_battery, 1)[0]
		initial = round(user_demands[item] * battery_level)
		initial = initial + 1 if (initial%2 == 1) else initial
		user_initial.append(int(initial))
		
def _get_arrival_time():
	for item in range(num_users):
		arr_time = df.loc[item, 'connectionTime'].split(' ')[4]
		# convert GMT to actual time
		split_time = arr_time.split(':')
		split_time[0] = ((int(split_time[0])) % 24) * 2 #str((int(split_time[0])) % 24)      
		split_time[1] = str(int(math.ceil(int(split_time[1]) / 30.0)) * 30)
		if int(split_time[1]) == 60:
			split_time[0] =  (split_time[0] + 1) % 48#str((int(split_time[0]) + 1) % 24) 
# 			split_time[1] = '00'
# 		split_time[2] = '00'
# 		user_arrivals.append(':'.join(split_time))
		user_arr_slots.append(split_time[0])

	

	# #####   Plotting   #####
	# conv_time = [datetime.datetime.strptime(i, "%H:%M:%S") for i in user_arrivals]
	# #define bin number
	# bin_nr = 288
	# fig, ax = plt.subplots(1,1)
	# # #create histogram, get bin position for label
	# N, bins, _patches = ax.hist(conv_time, bins = bin_nr)
	# # We'll color code by height, but you could use any scalar
	# fracs = N / N.max()
	
	# # we need to normalize the data to 0..1 for the full range of the colormap
	# norm = colors.Normalize(fracs.min(), fracs.max())

	# # Now, we'll loop through our objects and set the color of each accordingly
	# for thisfrac, thispatch in zip(fracs, _patches):
		# color = plt.cm.viridis(norm(thisfrac))
		# thispatch.set_facecolor(color)
		
	# # #reformat bin label into format hour:minute
	# ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
	# plt.show()
	
	
	
def _convert_time_slot():
	for slot in user_arrivals:
		temp = slot.split(':')
		slot_num = (int(temp[0]) * 6) + int(int(temp[1]) / 10)
		print(slot)
		user_arr_slots.append(slot_num)


# Generate and extract all the data	
_get_energy_demand_deadline()
_generate_power_modes()
_generate_kappa()
# _generate_arrival_time()
_generate_initial_energy()
_get_arrival_time()
# _convert_time_slot()
_generate_agg_id()


# Write to a csv file
df = pd.DataFrame()
df['arrival_time'] = user_arr_slots
df['agg_id'] = user_agg_id
df['energy_demand'] = user_demands
df['energy_initial'] = user_initial
df['deadline'] = user_deadlines
df['mobility_flag'] = [1 for i in range(num_users)]
df['kappa'] = user_priorities
df['power_modes'] = user_power_modes
df.to_csv('device.csv', index=False)
