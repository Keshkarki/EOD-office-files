import numpy as np
import pandas as pd
import datetime as dt
import os

pd.set_option('display.max_columns',None)
#variables

# Set the display width option
pd.set_option('display.width', 1000)


date = '2020-01-01'      
datestr = date.split('-')[0]
start_time = '09:15'
entry_time = '09:20'
exit_time = '15:15'
end_time = '15:20'
entry_side = 'sell'

underlying = 'BANKNIFTY'
underlying_strike_diff = 100 if underlying == 'BANKNIFTY' else 50
OTM_points = 100
exp_period = 'currWeek_exp_dt'

Sl_pct = 0.2  #0.2 -> 20%
tgt_pct = 0.8  #0.8 --> 80%

#conversion
date_dt = pd.to_datetime(date).date()
entry_time_dt = pd.to_datetime(entry_time).time()
exit_time_dt = pd.to_datetime(exit_time).time()
end_time_dt = pd.to_datetime(end_time).time()

#Main df file reading
df = pd.read_csv('C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\BANKNIFTY.csv',header=None)
df.rename(columns={
                0 : 'date',
                1 : 'time',
                2 : 'open',
                3 : 'high',
                4 : 'low',
                5 : 'close'
},inplace=True)
df['date'] = df['date'].astype('str')
datetime = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y%m%d %H:%M')
df.insert(1,'datetime',datetime) 
df['date'] = pd.to_datetime(df['date'])
df.set_index('datetime',inplace=True)
df= df.between_time('09:15:00', '15:29:00')
#Reading exp detail file
weekly_exp_df = pd.read_csv("Weekly_exp_dates.csv", usecols=['Exp_date'])
weekly_exp_df['Exp_date'] = pd.to_datetime(weekly_exp_df['Exp_date'], format='%d-%b-%y')
weekly_exp_df['day'] = weekly_exp_df['Exp_date'].dt.day
weekly_exp_df['monthly_exp'] = False
for i in range(len(weekly_exp_df) - 1):
    if weekly_exp_df.loc[i, 'day'] > weekly_exp_df.loc[i+1, 'day']:
        weekly_exp_df.loc[i, 'monthly_exp'] = True
monthly_exp_df = pd.DataFrame()
monthly_exp_df = weekly_exp_df.loc[(weekly_exp_df['monthly_exp'] == True), ['Exp_date', 'day']]
df_weekly_list = weekly_exp_df[['Exp_date']]
df_monthly_list = monthly_exp_df[['Exp_date']]
#making newe dataframe
df_datelist = pd.DataFrame(df['date'].unique(), columns = ['date'])
df_datelist[['currWeek_exp_dt', 'nextWeek_exp_dt', 'farWeek_exp_dt','currMonth_exp_dt', 'nextMonth_exp_dt', 'farMonth_exp_dt' ]] = np.NaN
for i in range(len(df_datelist)):
    df2 = df_weekly_list.loc[df_weekly_list['Exp_date'] >= df_datelist['date'][i]]
    df_datelist.loc[i,'currWeek_exp_dt'] = df2['Exp_date'].values[0]
    df_datelist.loc[i,'nextWeek_exp_dt'] = df2['Exp_date'].values[1]
    df_datelist.loc[i,'farWeek_exp_dt'] = df2['Exp_date'].values[2]
    df3 = df_monthly_list.loc[df_monthly_list['Exp_date'] >= df_datelist['date'][i]]
    df_datelist.loc[i,'currMonth_exp_dt'] = df3['Exp_date'].values[0]
    df_datelist.loc[i,'nextMonth_exp_dt'] = df3['Exp_date'].values[1]
    df_datelist.loc[i,'farMonth_exp_dt'] = df3['Exp_date'].values[2]
    pass    
    
merged_df = pd.merge(df,df_datelist,how='left', on='date')
merged_df['currWeek_exp_dt'] = pd.to_datetime(merged_df['currWeek_exp_dt']).dt.date
merged_df['nextWeek_exp_dt'] = pd.to_datetime(merged_df['nextWeek_exp_dt']).dt.date
merged_df['farWeek_exp_dt'] = pd.to_datetime(merged_df['farWeek_exp_dt']).dt.date
merged_df['currMonth_exp_dt'] = pd.to_datetime(merged_df['currMonth_exp_dt']).dt.date
merged_df['nextMonth_exp_dt'] = pd.to_datetime(merged_df['nextMonth_exp_dt']).dt.date
merged_df['farMonth_exp_dt'] = pd.to_datetime(merged_df['farMonth_exp_dt']).dt.date

merged_df['date'] = merged_df['date'].astype(str)
merged_df['time'] = merged_df['time'].astype(str)
datetime = pd.to_datetime(merged_df['date'] + ' ' + merged_df['time'], format='mixed', dayfirst=True)
df.index = pd.to_datetime(df.index)
merged_df.insert(0,'datetime',datetime) 
merged_df.set_index('datetime',inplace=True)
merged_df.drop(columns=['date','time'],inplace=True)
merged_df = merged_df.loc[merged_df.index.date == date_dt]

# PART-A ---->calculating ATM_Strike_price -->closed 100 
merged_df.insert(4,'ATMStrPr',round(merged_df['close'],-2))

def CE_strike_prices(entry_time_dt,date_dt):
    return str(round(merged_df.loc[(merged_df.index.time == entry_time_dt) & (merged_df.index.date == date_dt), 'ATMStrPr'].values[0] + OTM_points))

def PE_strike_prices(entry_time_dt,date_dt):
    return str(round(merged_df.loc[(merged_df.index.time == entry_time_dt) & (merged_df.index.date == date_dt), 'ATMStrPr'].values[0] - OTM_points))

CE_stp = CE_strike_prices(entry_time_dt,date_dt)
PE_stp = PE_strike_prices(entry_time_dt,date_dt)


# PART-B --> calculating expiry date
def exp_date_loc(entry_time_dt,date_dt):
    result= merged_df.loc[(merged_df.index.time == entry_time_dt) & (merged_df.index.date == date_dt)][exp_period]
    result = result.values[0]
    date = pd.to_datetime(result)
    formatted_date = date.strftime('%y%m%d')
    return formatted_date
exp_date = exp_date_loc(entry_time_dt,date_dt)
# print(exp_date)



ce_symbol = underlying+exp_date+CE_stp+'CE'
ce_symbol = f"{ce_symbol}"

pe_symbol = underlying+exp_date+PE_stp+'PE'
pe_symbol = f"{pe_symbol}"
print(ce_symbol)
print(pe_symbol)
