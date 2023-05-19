import numpy as np
import pandas as pd
import datetime as dt

#variables
entryDaysFromExpiry = 0
exitDaysFromExpiry = 0
entryTime = '15:15'
exitTime = '15:15'
underlying = 'NIFTY'            #dict
strikeDiff = 250                   #dict
underlyingStrikeDiff = 50                #dict

#dictionary



df = pd.read_csv('Weekly_exp_dates.csv',usecols=['Exp_date'])
df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')

df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=entryDaysFromExpiry)      #so we can have time delta
df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
df['entryDt'] = df['entry_date']+' '+entryTime
df['entryDt'] =  pd.to_datetime(df['entryDt'])
df['date'] = df['entryDt'].dt.date
df['time'] = df['entryDt'].dt.date
df.set_index('entryDt',inplace=True)
df = df[['expDateDt', 'date','time']]

print(df)