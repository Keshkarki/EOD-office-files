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
df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')

df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=entryDaysFromExpiry)      #so we can have time delta
df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
df['entryDt'] = df['entry_date']+' '+entryTime
df['entryDt'] =  pd.to_datetime(df['entryDt'])
df['date'] = df['entryDt'].dt.date
df['time'] = df['entryDt'].dt.date
df.set_index('entryDt',inplace=True)
df = df[['expDateDt', 'date','time']]

# print(df)



#Part2- Banknifty DAtaframe ###################################################################
df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)
df2.rename(columns={
                    0   : 'date',
                    1   : 'time',
                    2   : 'open',
                    3   : 'high',
                    4   : 'low',
                    5   : 'close'
},inplace=True)
df2['date'] = pd.to_datetime(df2['date'],format='%Y%m%d').dt.date.astype(str)
df2['datetime'] = df2['date'] + ' ' + df2['time']
df2['datetime'] = pd.to_datetime(df2['datetime'])
df2.set_index('datetime',inplace=True)
# print(df2)

#Part3 taking vaues from banknifty using merge #########################################################
merged_df = pd.merge(df,df2['close'], left_index=True,right_index=True, how='left')
# print(merged_df)

#adding this new column value taken from merged df close column to our df
df['BANKNIFTY_price'] = merged_df['close']

#column --> CE_strike and PE_strike
df['CE_strike'] = (round(df['BANKNIFTY_price']/underlyingStrikeDiff)*underlyingStrikeDiff + strikeDiff).astype(int)
df['PE_strike'] = (round(df['BANKNIFTY_price']/underlyingStrikeDiff)*underlyingStrikeDiff - strikeDiff).astype(int)




#Part4 -Creating Symbol for reading Option file ###############################################################
#Note format underlying+yymmdd+strikeprice+option(CE/PE)
yymmdd =  df.index.strftime('%y%m%d')
strikepriceCE = df['CE_strike'].astype('str')
strikepricePE = df['PE_strike'].astype('str')

df['symbolCE'] = underlying+yymmdd+strikepriceCE+'CE'
df['symbolPE'] = underlying+yymmdd+strikepricePE+'PE'
print(df)



#Part5 - Reading realtive option file for each symbol
# reading options
# rel_CE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{df['date'].iloc[0]}\\{underlying} Options\\{df['symbolCE'].iloc[0]}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

# rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'],format='%Y%m%d').dt.date
# rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'])
# rel_CE_df['CEdate'] = rel_CE_df['CEdate'].astype('str')
# CEdatetime = pd.to_datetime(rel_CE_df['CEdate'] + ' ' + rel_CE_df['CEtime'], format='%Y-%m-%d %H:%M')
# rel_CE_df.set_index(CEdatetime,inplace=True)
# print(rel_CE_df)

print(df['date'].iloc[0])