import numpy as np
import pandas as pd
import datetime as dt

#variables
entryDaysFromExpiry = 0
exitDaysFromExpiry = 0
entryTime = '15:15'
exitTime = '15:15'
strikeDiff = 250                 
underlyingStrikeDiff = 50              

underlying = 'BANKNIFTY'
underlying_strike_diff = 100 if underlying == 'BANKNIFTY' else 50
OTM_points = 100


#Part1 -Creating main dataframe ##########################################################
df = pd.read_csv('Weekly_exp_dates.csv',usecols=['Exp_date'])
# df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')

# df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=entryDaysFromExpiry)      #so we can have time delta
# df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
# df['entryDt'] = df['entry_date']+' '+entryTime
# df['entryDt'] =  pd.to_datetime(df['entryDt'])
# df['date'] = df['entryDt'].dt.date
# df['time'] = df['entryDt'].dt.date
# df.set_index('entryDt',inplace=True)
# df = df[['expDateDt', 'date','time']]

print(df)