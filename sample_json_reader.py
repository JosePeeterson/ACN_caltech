import json

with open('acn.json') as f:
  data = json.load(f)

Tot_chrg_stns = len(data['results'])

chrg_loc = {'location': [], 'lat': [], 'lng': []}

for i in range(Tot_chrg_stns):
    stn = data['results'][i]
    chrg_loc['location'].append(stn['public_name'])
    chrg_loc['lat'].append(stn['lat'])
    chrg_loc['lng'].append(stn['lng'])
    #print(chrg_loc['location'][i])
    #print(chrg_loc['lat'][i])
    #print(chrg_loc['lng'][i])


with open('charging_locations.json', 'w') as json_file:
  json.dump(chrg_loc, json_file)

