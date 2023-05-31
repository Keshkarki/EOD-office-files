# -*- coding: utf-8 -*-
"""
Backtest options from TrueData 
Underlying data is cleaned to include respective expiries (weekly and monthly both - curr, next, far)
"""

#%%

import pandas as pd
import time as tm
from datetime import time
import datetime
import numpy as np
import csv


#%%
underlying = 'NIFTY'
underlying_strike_diff = 50 if underlying == 'NIFTY' else 100
margin_per_lot = 160000 if underlying == 'NIFTY' else 175000
# op_range_start_time = '09:15'
# op_range_end_time = '09:19'
Entry_time = '09:19'
Square_off_time = '15:17'
CE_strike_distance = 0      # distance from ATM (0 is ATM)
PE_strike_distance = 0
Expiry_period = 'currWeek'
lot_size = 50 if underlying == 'NIFTY' else 25

CE_ISL_pct = 65    #(25 for 25 percent)
PE_ISL_pct = 65
exit_slippage_pct = 2
mtm_SL_pct = 0.4   #(% of underlying)

start_date = '2021-01-01'
end_date = '2022-12-30'
backtest_period = 2 # no of years (can also be calculated)

Entry_time_formatted = datetime.datetime.strptime(Entry_time, '%H:%M')
Square_off_time_formatted = datetime.datetime.strptime(Square_off_time, '%H:%M')
start_date_formatted = datetime.datetime.strptime(start_date, '%Y-%m-%d')
end_date_formatted = datetime.datetime.strptime(end_date, '%Y-%m-%d')

##%%
underlying_df = pd.read_csv(f'C:/Users/NRD/Downloads/Trading/Data/{underlying}_spot_withExpiries.csv')
# print(underlying_df)
##%%
df = underlying_df[['date','time', 'close','tm_stamp', 'currWeek_exp_dt',	'nextWeek_exp_dt',	'farWeek_exp_dt',	'currMonth_exp_dt',	'nextMonth_exp_dt',	'farMonth_exp_dt']].copy()
df['time_formatted'] = pd.to_datetime(df['time'], format = '%H:%M')
df['date_formatted'] = pd.to_datetime(df['date'], format = '%Y-%m-%d')
df['tm_stamp'] = pd.to_datetime(df['tm_stamp'], format = '%Y-%m-%d %H:%M' )
df = df[(df['date_formatted'] >= start_date_formatted) & (df['date_formatted'] <= end_date_formatted) ].copy()
df = df[(df['time_formatted'] >= Entry_time_formatted) & (df['time_formatted'] <= Square_off_time_formatted) ].copy()
# print(df)
date_list = df['date_formatted'].unique()
month_list = df['date_formatted'].dt.month.unique()
year_list = df['date_formatted'].dt.year.unique()




##%%
Daily_Results = pd.DataFrame()
for i in range(len(date_list)):
    # i = date_list[0]
    # print(date_list[i])
    intra_df = df[df['date_formatted']==date_list[i]]
    entry_spot = intra_df.loc[intra_df['time_formatted'] ==Entry_time_formatted,'close' ].iloc[0]
    ATM_strike =   round(entry_spot/underlying_strike_diff)*underlying_strike_diff
    CE_Sell_strike = ATM_strike + CE_strike_distance
    PE_Sell_strike = ATM_strike - PE_strike_distance
    mtm_SL_points = round(entry_spot*(mtm_SL_pct/100),2)
    
    intra_df = intra_df.assign(entry_spot = entry_spot, CE_Sell_strike = CE_Sell_strike, PE_Sell_strike = PE_Sell_strike )
    # intra_df.loc[:,['entry_spot', 'CE_Sell_strike', 'PE_Sell_strike']] = [entry_spot,CE_Sell_strike,PE_Sell_strike]
    intra_df.reset_index(inplace = True)
    # print(intra_df['date'])
    rel_expiry = intra_df[f'{Expiry_period}_exp_dt'].values[0]
    rel_expiry = datetime.datetime.strptime(rel_expiry, '%Y-%m-%d').strftime('%y%m%d')
    rel_date = intra_df['date'].values[0]
    rel_date = datetime.datetime.strptime(rel_date, '%Y-%m-%d')
    rel_date = rel_date.strftime('%Y%m%d')
    rel_data_year = intra_df['date'][0][:4]
    CE_file_name = str(underlying + rel_expiry + str(int(CE_Sell_strike)) + 'CE')
    PE_file_name = str(underlying + rel_expiry + str(int(PE_Sell_strike)) + 'PE')
    rel_CE_df = pd.read_csv(f'C:/Users/NRD/Downloads/Trading/Data/TrueData/NF_BNF_2020_21_22/NIFTY & BANKNIFTY Options Data/{rel_data_year}/{underlying} Options/{CE_file_name}.csv')
    rel_CE_df.columns = ['CEdate', 'CEtime','CEopen','CEhigh','CElow', 'CEclose','CEvolume','CEoi']
    rel_CE_df['CEtime_formatted'] = pd.to_datetime(rel_CE_df['CEtime'], format = '%H:%M')
    rel_CE_df = rel_CE_df[rel_CE_df['CEdate'].astype(str) == rel_date].copy()
    # rel_CE_df['CE_day_high'] = rel_CE_df['CEhigh'].cummax()
    # rel_CE_df['CE_day_low'] = rel_CE_df['CElow'].cummin()
    rel_PE_df = pd.read_csv(f'C:/Users/NRD/Downloads/Trading/Data/TrueData/NF_BNF_2020_21_22/NIFTY & BANKNIFTY Options Data/{rel_data_year}/{underlying} Options/{PE_file_name}.csv')
    rel_PE_df.columns = ['PEdate', 'PEtime','PEopen','PEhigh','PElow', 'PEclose','PEvolume','PEoi']
    rel_PE_df['PEtime_formatted'] = pd.to_datetime(rel_PE_df['PEtime'], format = '%H:%M')
    rel_PE_df = rel_PE_df[rel_PE_df['PEdate'].astype(str) == rel_date].copy()
    # rel_PE_df['PE_day_high'] = rel_PE_df['PEhigh'].cummax()
    # rel_PE_df['PE_day_low'] = rel_PE_df['PElow'].cummin()
    # intra_df_merged = intra_df.merge(rel_CE_df, how='inner', left_on = 'time', right_on = 'CEtime')
    intra_df_merged = pd.merge(intra_df, rel_CE_df, left_on='time_formatted', right_on = 'CEtime_formatted').fillna(method='ffill')
    intra_df_merged = pd.merge(intra_df_merged, rel_PE_df, left_on='time_formatted', right_on = 'PEtime_formatted').fillna(method='ffill')
    intra_df_merged.drop(['index'], axis = 1, inplace = True)

    CE_Entry_px = intra_df_merged['CEclose'][0]
    CE_ISL = round(CE_Entry_px*(1+CE_ISL_pct/100),2)
    PE_Entry_px = intra_df_merged['PEclose'][0]
    PE_ISL = round(PE_Entry_px*(1+PE_ISL_pct/100),2)
    
    intra_df_merged['CE_Entry_px'] = CE_Entry_px
    intra_df_merged['CE_ISL'] = CE_ISL
    intra_df_merged['CE_SL_px'] = CE_ISL
    intra_df_merged['PE_Entry_px'] = PE_Entry_px
    intra_df_merged['PE_ISL'] = PE_ISL
    intra_df_merged['PE_SL_px'] = PE_ISL

    intra_df_merged['CE_Entry_taken'] = np.where(intra_df_merged['time_formatted'] > Entry_time_formatted, 1,0 )
    intra_df_merged['CE_day_high'] =   intra_df_merged.groupby(['CE_Entry_taken'])['CEhigh'].cummax()
    intra_df_merged['CE_day_high'] =   np.where( (intra_df_merged['CE_Entry_taken'] == 0),0, intra_df_merged.groupby(['CE_Entry_taken'])['CEhigh'].cummax())
    #intra_df_merged['CE_day_low'] =   np.where( (intra_df_merged['CE_Entry_taken'] == 1), intra_df_merged['CElow'].cummin(),0)  .. this one will also give a value in the row where there is no entry
    intra_df_merged['PE_Entry_taken'] = np.where(intra_df_merged['time_formatted'] > Entry_time_formatted, 1,0 )
    intra_df_merged['PE_day_high'] =   intra_df_merged.groupby(['PE_Entry_taken'])['PEhigh'].cummax()
    intra_df_merged['PE_day_high'] =   np.where( (intra_df_merged['PE_Entry_taken'] == 0),0, intra_df_merged.groupby(['PE_Entry_taken'])['PEhigh'].cummax())
    #intra_df_merged['PE_day_low'] =   np.where( (intra_df_merged['PE_Entry_taken'] == 1), intra_df_merged['PElow'].cummin(),0)  .. this one will also give a value in the row where there is no entry
    intra_df_merged['CE_mtm_high'] = 0  
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'CE_mtm_high'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CElow']
    intra_df_merged['CE_mtm_low'] = 0  
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'CE_mtm_low'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CEhigh']
    intra_df_merged['PE_mtm_high'] = 0  
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'PE_mtm_high'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PElow']
    intra_df_merged['PE_mtm_low'] = 0  
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'PE_mtm_low'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PEhigh']
    intra_df_merged['overall_mtm_low1'] = intra_df_merged['CE_mtm_high'] + intra_df_merged['PE_mtm_low']
    intra_df_merged['overall_mtm_low2']  = intra_df_merged['CE_mtm_low'] + intra_df_merged['PE_mtm_high']
    intra_df_merged['overall_mtm_low'] = intra_df_merged[['overall_mtm_low1','overall_mtm_low2']].min(axis=1)
    intra_df_merged['overall_mtm_mdd'] = intra_df_merged['overall_mtm_low'].cummin()
    
    intra_df_merged['overall_mtm_hit_status'] = 0   #(0 for not hit and 1 for hit)
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['overall_mtm_mdd'] < -mtm_SL_points), 'overall_mtm_hit_status'  ] = 1
    intra_df_merged['mtm_hit_points'] = -round(mtm_SL_points*(1+(exit_slippage_pct/2)/100),2 )       # exit slippage to applies only on half since one leg will be out already
    # intra_df_merged.loc[(intra_df_merged['overall_mtm_hit_status'] == 1) ,'mtm_hit_points'  ] = -round(mtm_SL_points*(1+(exit_slippage_pct/2)/100),2 )       # exit slippage to applies only on half since one leg will be out already
    
    # print(intra_df_merged[['overall_mtm_low1','overall_mtm_low2', 'overall_mtm_low','overall_mtm_mdd' ]])
    
    # intra_df_merged['CE_SL_hit'] = np.NaN
    intra_df_merged['CE_SL_hit'] = np.where((intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_day_high'] >= intra_df_merged['CE_SL_px']), 1,0 )
    # intra_df_merged['CE_SL_hit'] = intra_df_merged['CE_SL_hit'].replace(to_replace=0, method = 'ffill')
    intra_df_merged['CE_status'] = np.NaN    #(NaN for not triggered yet, 1 for in position, 0 is exited)
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 0), 'CE_status'  ] = 1
    intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 1), 'CE_status'  ] = 0
    # intra_df_merged['CE_status'] = np.where((intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 0), 1,0)
    intra_df_merged['CE_mtm'] = 0  
    intra_df_merged.loc[(intra_df_merged['CE_status'] == 1), 'CE_mtm'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CEclose']
    intra_df_merged.loc[(intra_df_merged['CE_status'] == 0), 'CE_mtm'] = round(intra_df_merged['CE_Entry_px'] - intra_df_merged['CE_SL_px']*(1+exit_slippage_pct/100) ,2)
    # intra_df_merged.loc[(intra_df_merged['time_formatted'] == Square_off_time_formatted), 'CE_mtm']
    
    # intra_df_merged['PE_SL_hit'] = np.NaN
    intra_df_merged['PE_SL_hit'] = np.where((intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_day_high'] >= intra_df_merged['PE_SL_px']), 1,0 )
    # intra_df_merged['PE_SL_hit'] = intra_df_merged['PE_SL_hit'].replace(to_replace=0, method = 'ffill')
    intra_df_merged['PE_status'] = np.NaN     #(NaN for not triggered yet, 1 for in position, 0 is exited)
    intra_df_merged.loc[(intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 0), 'PE_status'  ] = 1
    intra_df_merged.loc[(intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 1), 'PE_status'  ] = 0
    # intra_df_merged['PE_status'] = np.where((intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 0), 1,0)
    intra_df_merged['PE_mtm'] = 0  
    intra_df_merged.loc[(intra_df_merged['PE_status'] == 1), 'PE_mtm'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PEclose']
    intra_df_merged.loc[(intra_df_merged['PE_status'] == 0), 'PE_mtm'] = round(intra_df_merged['PE_Entry_px'] - intra_df_merged['PE_SL_px']*(1+exit_slippage_pct/100) ,2)
    # intra_df_merged.loc[(intra_df_merged['time_formatted'] == Square_off_time_formatted), 'PE_mtm']
    
    intra_df_merged['overall_CE_PE_mtm'] = intra_df_merged['CE_mtm'] + intra_df_merged['PE_mtm'] 
    intra_df_merged['overall_mtm'] = intra_df_merged[['overall_CE_PE_mtm', 'mtm_hit_points']].max(axis=1)
    
    Daily_Results.loc[i,['spot_close','date_formatted', 'overall_mtm']] =  intra_df_merged.loc[intra_df_merged.index[-1], ['close','date_formatted','overall_mtm']].tolist()
    

    pass
    

##%%
Daily_Results['cum_mtm'] = Daily_Results['overall_mtm'].cumsum()
Daily_Results['peak_mtm'] = Daily_Results['cum_mtm'].cummax()

Daily_Results['dd'] = Daily_Results['cum_mtm'] - Daily_Results['peak_mtm']
Max_dd = round(Daily_Results['dd'].min(),2)
Total_ret = round(Daily_Results['cum_mtm'].iloc[-1],2)
Total_ret_pct = round((Total_ret*lot_size/margin_per_lot)*100,2)
Avg_ret_pct = round(Total_ret_pct/ backtest_period,2)
MDD_pct = round((Max_dd*lot_size/margin_per_lot)*100, 2)
calmar = round((Total_ret/backtest_period)/-Max_dd,2)


##%%
annual_results = pd.DataFrame()
monthly_results = pd.DataFrame()
monthly_dict = {}
for i in range(len(year_list)):
    yr = year_list[i]
    annual_daily_result = Daily_Results[pd.to_datetime(Daily_Results.date_formatted).dt.year.eq(yr)]
    annual_daily_result = annual_daily_result[['spot_close', 'date_formatted', 'overall_mtm']].copy()
    annual_daily_result['month'] = pd.to_datetime(annual_daily_result.date_formatted).dt.month
    annual_daily_result['cum_mtm'] = annual_daily_result['overall_mtm'].cumsum()
    annual_daily_result['peak_mtm'] = annual_daily_result['cum_mtm'].cummax()
    annual_daily_result['dd'] = annual_daily_result['cum_mtm'] - annual_daily_result['peak_mtm']
    month_list = annual_daily_result['month'].unique()
    monthly_returns_list = annual_daily_result.groupby('month')['overall_mtm'].sum().round(2).to_list()
    for mn in range(len(month_list)):
        monthly_dict[month_list[mn]] = monthly_returns_list[mn]
    annual_Max_dd = round(annual_daily_result['dd'].min(),2)
    annual_total_ret = round(annual_daily_result['cum_mtm'].iloc[-1],2)
    annual_calmar = round(annual_total_ret/-Max_dd,2)
    annual_ret_pct = round(annual_total_ret*100*lot_size/margin_per_lot,2)
    max_dd_pct = round(annual_Max_dd*100*lot_size/margin_per_lot,2)
    annual_results.loc[i,['Year','Return_pct', 'MDD_pct','mtm_points', 'Max_dd_points', 'Calmar']]    = [int(yr),annual_ret_pct,max_dd_pct,annual_total_ret,annual_Max_dd,annual_calmar]
    monthly_results.loc[i,'Year'] = int(yr)
    for k,v in monthly_dict.items():
        monthly_results.loc[i,k] = v
print('\n')
print('underlying  ', underlying, '.  Entry_time  ', Entry_time, '.  Square_off_time', Square_off_time, '.  CE_strike_distance  ', CE_strike_distance, '.  PE_strike_distance  ', PE_strike_distance  )
print('Total_ret  ' , Total_ret ,'.  Max_dd  ' ,Max_dd ,'.  Total_ret_pct  ' ,Total_ret_pct ,'.  Avg_ret_pct  ' ,Avg_ret_pct ,'.  MDD_pct  ' ,MDD_pct ,'.  calmar  ' ,calmar)

print('\n',annual_results)
print('\n',monthly_results)
#%%
#%%

#%%
#%%

#%%
#%%

#%%
#%%

#%%
#%%

#%%

#%%
xx = annual_daily_result.groupby('month')['overall_mtm'].sum().round(2)
print(xx.columns)
#%%

#%%

#%%

#%%



#%%
i = date_list[0]
intra_df = df[df['date_formatted']==i]
entry_spot = intra_df.loc[intra_df['time_formatted'] ==Entry_time_formatted,'close' ].iloc[0]
ATM_strike =   round(entry_spot/underlying_strike_diff)*underlying_strike_diff
CE_Sell_strike = ATM_strike + CE_strike_distance
PE_Sell_strike = ATM_strike - PE_strike_distance
mtm_SL_points = round(entry_spot*(mtm_SL_pct/100),2)

#%%

intra_df = intra_df.assign(entry_spot = entry_spot, CE_Sell_strike = CE_Sell_strike, PE_Sell_strike = PE_Sell_strike )
# intra_df.loc[:,['entry_spot', 'CE_Sell_strike', 'PE_Sell_strike']] = [entry_spot,CE_Sell_strike,PE_Sell_strike]
intra_df.reset_index(inplace = True)
# print(intra_df['date'])

#%%
# rel_expiry = intra_df.loc[0, f'{Expiry_period}_exp_dt']

rel_expiry = intra_df[f'{Expiry_period}_exp_dt'].values[0]
rel_expiry = datetime.datetime.strptime(rel_expiry, '%Y-%m-%d').strftime('%y%m%d')
rel_date = intra_df['date'].values[0]
rel_date = datetime.datetime.strptime(rel_date, '%Y-%m-%d')
rel_date = rel_date.strftime('%Y%m%d')
rel_data_year = intra_df['date'][0][:4]
CE_file_name = str(underlying + rel_expiry + str(int(CE_Sell_strike)) + 'CE')
PE_file_name = str(underlying + rel_expiry + str(int(PE_Sell_strike)) + 'PE')
rel_CE_df = pd.read_csv(f'C:/Users/NRD/Downloads/Trading/Data/TrueData/NF_BNF_2020_21_22/NIFTY & BANKNIFTY Options Data/{rel_data_year}/{underlying} Options/{CE_file_name}.csv')
rel_CE_df.columns = ['CEdate', 'CEtime','CEopen','CEhigh','CElow', 'CEclose','CEvolume','CEoi']
rel_CE_df['CEtime_formatted'] = pd.to_datetime(rel_CE_df['CEtime'], format = '%H:%M')
rel_CE_df = rel_CE_df[rel_CE_df['CEdate'].astype(str) == rel_date].copy()
# rel_CE_df['CE_day_high'] = rel_CE_df['CEhigh'].cummax()
# rel_CE_df['CE_day_low'] = rel_CE_df['CElow'].cummin()
rel_PE_df = pd.read_csv(f'C:/Users/NRD/Downloads/Trading/Data/TrueData/NF_BNF_2020_21_22/NIFTY & BANKNIFTY Options Data/{rel_data_year}/{underlying} Options/{PE_file_name}.csv')
rel_PE_df.columns = ['PEdate', 'PEtime','PEopen','PEhigh','PElow', 'PEclose','PEvolume','PEoi']
rel_PE_df['PEtime_formatted'] = pd.to_datetime(rel_PE_df['PEtime'], format = '%H:%M')
rel_PE_df = rel_PE_df[rel_PE_df['PEdate'].astype(str) == rel_date].copy()
# rel_PE_df['PE_day_high'] = rel_PE_df['PEhigh'].cummax()
# rel_PE_df['PE_day_low'] = rel_PE_df['PElow'].cummin()

#%%
# intra_df_merged = intra_df.merge(rel_CE_df, how='inner', left_on = 'time', right_on = 'CEtime')
intra_df_merged = pd.merge(intra_df, rel_CE_df, left_on='time_formatted', right_on = 'CEtime_formatted').fillna(method='ffill')
intra_df_merged = pd.merge(intra_df_merged, rel_PE_df, left_on='time_formatted', right_on = 'PEtime_formatted').fillna(method='ffill')
intra_df_merged.drop(['index'], axis = 1, inplace = True)

print(intra_df_merged)
#%%
CE_Entry_px = intra_df_merged['CEclose'][0]
CE_ISL = round(CE_Entry_px*(1+CE_ISL_pct/100),2)

PE_Entry_px = intra_df_merged['PEclose'][0]
PE_ISL = round(PE_Entry_px*(1+PE_ISL_pct/100),2)

intra_df_merged['CE_Entry_px'] = CE_Entry_px
intra_df_merged['CE_ISL'] = CE_ISL
intra_df_merged['CE_SL_px'] = CE_ISL
intra_df_merged['PE_Entry_px'] = PE_Entry_px
intra_df_merged['PE_ISL'] = PE_ISL
intra_df_merged['PE_SL_px'] = PE_ISL

#%%
intra_df_merged['CE_Entry_taken'] = np.where(intra_df_merged['time_formatted'] > Entry_time_formatted, 1,0 )
intra_df_merged['CE_day_high'] =   intra_df_merged.groupby(['CE_Entry_taken'])['CEhigh'].cummax()
intra_df_merged['CE_day_high'] =   np.where( (intra_df_merged['CE_Entry_taken'] == 0),0, intra_df_merged.groupby(['CE_Entry_taken'])['CEhigh'].cummax())
#intra_df_merged['CE_day_low'] =   np.where( (intra_df_merged['CE_Entry_taken'] == 1), intra_df_merged['CElow'].cummin(),0)  .. this one will also give a value in the row where there is no entry
intra_df_merged['PE_Entry_taken'] = np.where(intra_df_merged['time_formatted'] > Entry_time_formatted, 1,0 )
intra_df_merged['PE_day_high'] =   intra_df_merged.groupby(['PE_Entry_taken'])['PEhigh'].cummax()
intra_df_merged['PE_day_high'] =   np.where( (intra_df_merged['PE_Entry_taken'] == 0),0, intra_df_merged.groupby(['PE_Entry_taken'])['PEhigh'].cummax())
#intra_df_merged['PE_day_low'] =   np.where( (intra_df_merged['PE_Entry_taken'] == 1), intra_df_merged['PElow'].cummin(),0)  .. this one will also give a value in the row where there is no entry
intra_df_merged['CE_mtm_high'] = 0  
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'CE_mtm_high'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CElow']
intra_df_merged['CE_mtm_low'] = 0  
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'CE_mtm_low'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CEhigh']
intra_df_merged['PE_mtm_high'] = 0  
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'PE_mtm_high'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PElow']
intra_df_merged['PE_mtm_low'] = 0  
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1), 'PE_mtm_low'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PEhigh']
intra_df_merged['overall_mtm_low1'] = intra_df_merged['CE_mtm_high'] + intra_df_merged['PE_mtm_low']
intra_df_merged['overall_mtm_low2']  = intra_df_merged['CE_mtm_low'] + intra_df_merged['PE_mtm_high']
intra_df_merged['overall_mtm_low'] = intra_df_merged[['overall_mtm_low1','overall_mtm_low2']].min(axis=1)
intra_df_merged['overall_mtm_mdd'] = intra_df_merged['overall_mtm_low'].cummin()

intra_df_merged['overall_mtm_hit_status'] = 0   #(0 for not hit and 1 for hit)
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['overall_mtm_mdd'] < -mtm_SL_points), 'overall_mtm_hit_status'  ] = 1
intra_df_merged['mtm_hit_points'] = -round(mtm_SL_points*(1+(exit_slippage_pct/2)/100),2 )       # exit slippage to applies only on half since one leg will be out already
# intra_df_merged.loc[(intra_df_merged['overall_mtm_hit_status'] == 1) ,'mtm_hit_points'  ] = -round(mtm_SL_points*(1+(exit_slippage_pct/2)/100),2 )       # exit slippage to applies only on half since one leg will be out already

# print(intra_df_merged[['overall_mtm_low1','overall_mtm_low2', 'overall_mtm_low','overall_mtm_mdd' ]])

# intra_df_merged['CE_SL_hit'] = np.NaN
intra_df_merged['CE_SL_hit'] = np.where((intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_day_high'] >= intra_df_merged['CE_SL_px']), 1,0 )
# intra_df_merged['CE_SL_hit'] = intra_df_merged['CE_SL_hit'].replace(to_replace=0, method = 'ffill')
intra_df_merged['CE_status'] = np.NaN    #(NaN for not triggered yet, 1 for in position, 0 is exited)
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 0), 'CE_status'  ] = 1
intra_df_merged.loc[(intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 1), 'CE_status'  ] = 0
# intra_df_merged['CE_status'] = np.where((intra_df_merged['CE_Entry_taken'] == 1) & (intra_df_merged['CE_SL_hit'] == 0), 1,0)
intra_df_merged['CE_mtm'] = 0  
intra_df_merged.loc[(intra_df_merged['CE_status'] == 1), 'CE_mtm'] = intra_df_merged['CE_Entry_px'] - intra_df_merged['CEclose']
intra_df_merged.loc[(intra_df_merged['CE_status'] == 0), 'CE_mtm'] = round(intra_df_merged['CE_Entry_px'] - intra_df_merged['CE_SL_px']*(1+exit_slippage_pct/100) ,2)
# intra_df_merged.loc[(intra_df_merged['time_formatted'] == Square_off_time_formatted), 'CE_mtm']

# intra_df_merged['PE_SL_hit'] = np.NaN
intra_df_merged['PE_SL_hit'] = np.where((intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_day_high'] >= intra_df_merged['PE_SL_px']), 1,0 )
# intra_df_merged['PE_SL_hit'] = intra_df_merged['PE_SL_hit'].replace(to_replace=0, method = 'ffill')
intra_df_merged['PE_status'] = np.NaN     #(NaN for not triggered yet, 1 for in position, 0 is exited)
intra_df_merged.loc[(intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 0), 'PE_status'  ] = 1
intra_df_merged.loc[(intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 1), 'PE_status'  ] = 0
# intra_df_merged['PE_status'] = np.where((intra_df_merged['PE_Entry_taken'] == 1) & (intra_df_merged['PE_SL_hit'] == 0), 1,0)
intra_df_merged['PE_mtm'] = 0  
intra_df_merged.loc[(intra_df_merged['PE_status'] == 1), 'PE_mtm'] = intra_df_merged['PE_Entry_px'] - intra_df_merged['PEclose']
intra_df_merged.loc[(intra_df_merged['PE_status'] == 0), 'PE_mtm'] = round(intra_df_merged['PE_Entry_px'] - intra_df_merged['PE_SL_px']*(1+exit_slippage_pct/100) ,2)
# intra_df_merged.loc[(intra_df_merged['time_formatted'] == Square_off_time_formatted), 'PE_mtm']

#%%

intra_df_merged['overall_CE_PE_mtm'] = intra_df_merged['CE_mtm'] + intra_df_merged['PE_mtm'] 
intra_df_merged['overall_mtm'] = intra_df_merged[['overall_CE_PE_mtm', 'mtm_hit_points']].max(axis=1)



Daily_Results = pd.DataFrame()
Daily_Results.loc[0,['date_formatted', 'overall_mtm']] =  intra_df_merged.loc[intra_df_merged.index[-1], ['date_formatted','overall_mtm']].tolist()

print(Daily_Results)
#%%

#%%

#%%


print(intra_df_merged.iloc[:,48:])
print(intra_df_merged.loc[intra_df_merged.index[-1], 'CE_mtm'])

#%%
print(intra_df_merged[['CE_mtm','PE_mtm', 'overall_mtm', 'mtm_hit_points']])

#%%


#%%


#%%
df = pd.read_csv('C:/Users/NRD\Downloads\Trading\Analysis/BNF_diff_opens_2021.csv')
print(df)

#%%
rr = list(df.loc[0])
print(rr)

#%%


#%%


#%%


#%%
rel_CE_df1 = rel_CE_df.copy()
rel_CE_df1['CE_day_high'] = rel_CE_df1['CEhigh'].cummax()
print(rel_CE_df1[['CEhigh','CE_day_high']].loc[5:25])

#%%


#%%


#%%


#%%


#%%


#%%


