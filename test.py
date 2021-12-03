import datetime
import dateutil
import pandas as pd

df = pd.read_csv('20210501-20210508 CAISO Average Price.csv')

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
    Minute_Elec_price[datetime_obj] = price

    j+=1
    if (j == 5):
        i+=1
        j=0

print(Minute_Elec_price)

datetime_obj = datetime_obj + datetime.timedelta(minutes=1)

print(datetime_obj)

t = "2012-05-21 5:3:00"

print(dateutil.parser.parse(t))


