import pandas as pd
from datetime import datetime 

df = pd.read_csv('20210522-20210531 CAISO Average Price.csv')

i=0
for d in df['date']:
    print(d)
    d_ob = datetime.strptime(d,'%m/%d/%Y %I:%M:%S %p' )
    print(d_ob)
    d_ob1 = datetime.strftime(d_ob,'%m/%d/%y %H:%M')
    df['date'][i] = d_ob1
    i+=1

print(df)

df.to_csv('20210522-20210531 CAISO Average Price.csv')
