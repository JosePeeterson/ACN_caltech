import matplotlib.pyplot as plt
import matplotlib.dates as md
import dateutil
import json

with open('acndata_1_week.json') as f:
    data = json.load(f)

len_events = len(data['_items'])

unique_space_id = []

for i in range(0, len_events):
    if ( data['_items'][i]['spaceID'] not in unique_space_id):
        unique_space_id.append(data['_items'][i]['spaceID'])

All_space_data = {}
k=0
for j in unique_space_id:
    con_time = []
    discon_time = []
    kw_req = []
    kw_del = []
    all_time_one_space_data = {}
    for i in range(0, len_events):
        if ( (data['_items'][i]['spaceID'] == j) ):
            con_time.append(data['_items'][i]['connectionTime'])
            discon_time.append(data['_items'][i]['disconnectTime'])
            if ( data['_items'][i]['userInputs'] != None):
                kw_req.append(data['_items'][i]['userInputs'][0]['kWhRequested'])
                kw_del.append(data['_items'][i]['userInputs'][0]['minutesAvailable'])
                k+=1

    all_time_one_space_data['kWhRequested'] = kw_req
    all_time_one_space_data['Connect_time'] = con_time
    all_time_one_space_data['Disconnect_time'] = discon_time
    all_time_one_space_data['Minutes_available'] = kw_del
    All_space_data[j] = all_time_one_space_data
    #print(j)

each_veh_connect_times = []
unique_connect_time_dates = []

for s in unique_space_id:
    # print(s)
    # print(len(All_space_data[s]['kWhRequested']))
    # print(len(All_space_data[s]['Minutes_available']))
    # print(len(All_space_data[s]['Disconnect_time']))
    # print(len(All_space_data[s]['Connect_time']))
    # print('\n')
    for d in All_space_data[s]['Connect_time']:
        date = d[5:16]
        if (date not in unique_connect_time_dates):
            unique_connect_time_dates.append(date)
    #print(All_space_data[s]['Connect_time'])



datestrings = []

hr_of_day = 00
min_of_day = 00

for d in unique_connect_time_dates:

    day_end = False

    while( not day_end):
        date_time = d[7:11] + "-" + "05" + "-" + d[0:2] + " " + str(hr_of_day) + ":" + str(min_of_day) + ":00"

        datestrings.append(date_time)

        min_of_day+=1
        if (min_of_day == 60):
            hr_of_day+=1
            min_of_day = 0
        if (hr_of_day == 24):
            hr_of_day = 0
            day_end = True

#print(datestrings)
dates = [dateutil.parser.parse(s) for s in datestrings]

plt_data = range(0,len(dates))

plt.subplots_adjust(bottom=0.2)
plt.xticks( rotation=25 )

ax=plt.gca()
ax.set_xticks(dates)

xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.xaxis.set_major_formatter(xfmt)
plt.plot(dates,plt_data, "o-")
plt.show()


