import numpy as np
import pandas as pd
import datetime as dt
import os

pd.set_option('display.max_columns',None)
#variables

# Set the display width option
pd.set_option('display.width', 1000)

date = '2021-03-18'      
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
print(date_dt)
print(type(date_dt))

entry_time_dt = pd.to_datetime(entry_time).time()
exit_time_dt = pd.to_datetime(exit_time).time()
end_time_dt = pd.to_datetime(end_time).time()


# looping it for all the dates ---------------------------------->
#taking unique dates 
# df = pd.read_csv('C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\BANKNIFTY.csv',header=None)

# df.rename(columns={0:'date'},inplace=True)
# df=pd.to_datetime(df['date'],format='%Y%m%d')
# df =df.apply(lambda x: x.strftime('%Y-%m-%d'))
# df_lst= df.values   # list created

# print(df_lst)

# unique_lst = []
# for item in df_lst[:4]:
#     if item not in unique_lst:
#         item = pd.to_datetime(item).date()
#         unique_lst.append(item)



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


for i in range(len(weekly_exp_df)):
    try:
        if weekly_exp_df.loc[i, 'day'] > weekly_exp_df.loc[i+1, 'day']:
            weekly_exp_df.loc[i, 'monthly_exp'] = True
        monthly_exp_df = pd.DataFrame()
        monthly_exp_df = weekly_exp_df.loc[(weekly_exp_df['monthly_exp'] == True), ['Exp_date', 'day']]
        df_weekly_list = weekly_exp_df[['Exp_date']]
        df_monthly_list = monthly_exp_df[['Exp_date']]

        #making newe dataframe
        df_datelist = pd.DataFrame(df['date'].unique(), columns = ['date'])
        df_datelist[['currWeek_exp_dt', 'nextWeek_exp_dt', 'farWeek_exp_dt','currMonth_exp_dt', 'nextMonth_exp_dt', 'farMonth_exp_dt' ]] = np.NaN

    except: 
        pass


for i in range(len(df_datelist)):
    try:
        df2 = df_weekly_list.loc[df_weekly_list['Exp_date'] >= df_datelist['date'][i]]
        df_datelist.loc[i,'currWeek_exp_dt'] = df2['Exp_date'].values[0]
        df_datelist.loc[i,'nextWeek_exp_dt'] = df2['Exp_date'].values[1]
        df_datelist.loc[i,'farWeek_exp_dt'] = df2['Exp_date'].values[2]
        df3 = df_monthly_list.loc[df_monthly_list['Exp_date'] >= df_datelist['date'][i]]

        df_datelist.loc[i,'currMonth_exp_dt'] = df3['Exp_date'].values[0]
        df_datelist.loc[i,'nextMonth_exp_dt'] = df3['Exp_date'].values[1]
        df_datelist.loc[i,'farMonth_exp_dt'] = df3['Exp_date'].values[2]
    
    except:
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

merged_df.to_csv('Hello3.csv')
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


# print(ce_symbol)
# print(pe_symbol)



# reading options
rel_CE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{datestr}\\{underlying} Options\\{ce_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'],format='%Y%m%d').dt.date
rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'])
rel_CE_df['CEdate'] = rel_CE_df['CEdate'].astype('str')
CEdatetime = pd.to_datetime(rel_CE_df['CEdate'] + ' ' + rel_CE_df['CEtime'], format='%Y-%m-%d %H:%M')
rel_CE_df.set_index(CEdatetime,inplace=True)

rel_CE_df=rel_CE_df.loc[date]




#Creating  CE_entryPrice column
CE_entryPriceValue = rel_CE_df.loc[rel_CE_df.index.time == entry_time_dt ]['CEclose'].values[0]


rel_CE_df['CEentryPrice'] = np.NaN
rel_CE_df.loc[rel_CE_df.index.time > entry_time_dt, 'CEentryPrice'] = CE_entryPriceValue

#Creating CEstoploss
rel_CE_df['CEstoploss'] =np.NaN
rel_CE_df.loc[rel_CE_df.index.time > entry_time_dt, 'CEstoploss'] = CE_entryPriceValue*(1+Sl_pct)

#Creating target
rel_CE_df['CEtarget'] = np.NaN
rel_CE_df.loc[rel_CE_df.index.time > entry_time_dt, 'CEtarget'] = CE_entryPriceValue*(1 - tgt_pct)


# #Creating CE_SL_hit
rel_CE_df['CE_SLhit'] = np.where(rel_CE_df['CEhigh'] >= rel_CE_df['CEstoploss'], 1, 0)

#Creating CE_Tgthit
rel_CE_df['CE_Tgthit'] = np.where(rel_CE_df['CElow'] <= rel_CE_df['CEtarget'], 1, 0)


#--->calculating CEhitstatus
#Creating hitType column whether SL/TGT/Squreoff
condition1 = rel_CE_df['CE_SLhit'] == 1
condition2 = rel_CE_df['CE_Tgthit']==1
condition3 = rel_CE_df.index.time == exit_time_dt



rel_CE_df['CEhitstatus'] = ''
rel_CE_df.loc[condition1, 'CEhitstatus'] = 'SL_hit'
rel_CE_df.loc[condition2, 'CEhitstatus'] = 'TGThit'
rel_CE_df.loc[condition3, 'CEhitstatus'] = 'squareoff'


#modified PEhitstatus column
first_non_null = rel_CE_df[rel_CE_df['CEhitstatus'] != '']['CEhitstatus'].iloc[0]
rel_CE_df['CEhitstatus'] = np.where(rel_CE_df['CEhitstatus'] != '', first_non_null,'')


# #--->Calcuating CEexitPrice column
rel_CE_df['CEexitPrice'] = np.NaN
rel_CE_df.loc[rel_CE_df['CEhitstatus'] == 'SL_hit','CEexitPrice'] = rel_CE_df['CEstoploss']
rel_CE_df.loc[rel_CE_df['CEhitstatus'] == 'TGThit','CEexitPrice'] = rel_CE_df['CEtarget']
rel_CE_df.loc[rel_CE_df['CEhitstatus'] == 'squareoff','CEexitPrice'] = rel_CE_df['CEclose']

#--->Calcuating CE_MTM column
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_MTM'] = np.where(condition, rel_CE_df['CEentryPrice'] - rel_CE_df['CEclose'], np.nan)

#--->Calcuating CE_highMTM (entryprice-low)
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_highMTM'] = np.where(condition, rel_CE_df['CEentryPrice'] - rel_CE_df['CElow'], np.nan)

#--->Calcuating CE_maxMTM
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_maxMTM'] = np.where(condition,np.where(rel_CE_df['CE_highMTM'].cummax() > 0 ,rel_CE_df['CE_highMTM'].cummax() ,np.nan),np.nan)

#--->Calcuating CE_lowMTM  (entryprice-high)
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_lowMTM'] = np.where(condition, rel_CE_df['CEentryPrice'] - rel_CE_df['CEhigh'], np.nan)

#--->Calcuating CE_minMTM
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_minMTM'] = np.where(condition,rel_CE_df['CE_lowMTM'].cummin(), np.nan)

#--->Calcuating CE_PnL column
condition = (rel_CE_df.index.time >= entry_time_dt) & (rel_CE_df.index.time <= end_time_dt)
rel_CE_df['CE_PnL'] = np.where(condition, rel_CE_df['CEentryPrice'] - rel_CE_df['CEexitPrice'], np.nan)
# print(rel_CE_df.tail(30))

# # #############################################################################################################

#Calculating for PE
rel_PE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{datestr}\\{underlying} Options\\{pe_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])

rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date
rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'])
rel_PE_df['PEdate'] = rel_PE_df['PEdate'].astype('str')
PEdatetime = pd.to_datetime(rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime'], format='%Y-%m-%d %H:%M')
rel_PE_df.set_index(PEdatetime,inplace=True)
rel_PE_df=rel_PE_df.loc[date]
rel_PE_df.drop(columns=['PEdate','PEtime'],inplace=True)

PE_entryPriceValue = rel_PE_df.loc[rel_PE_df.index.time == entry_time_dt ]['PEclose'].values[0]

rel_PE_df['PEentryPrice'] = np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEentryPrice'] = PE_entryPriceValue

#Creating PEstoploss
rel_PE_df['PEstoploss'] =np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEstoploss'] = PE_entryPriceValue*(1+Sl_pct)

#Creating target
rel_PE_df['PEtarget'] = np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEtarget'] = PE_entryPriceValue*(1 - tgt_pct)

#Creating PE_SL_hit
rel_PE_df['PE_SLhit'] = np.where(rel_PE_df['PEhigh'] >= rel_PE_df['PEstoploss'], 1, 0)

#Creating PE_Tgthit
rel_PE_df['PE_Tgthit'] = np.where(rel_PE_df['PElow'] <= rel_PE_df['PEtarget'], 1, 0)

#--->calculating PEhitstatus
#Creating hitType column whether SL/TGT/Squreoff
condition1 = rel_PE_df['PE_SLhit'] == 1
condition2 = rel_PE_df['PE_Tgthit']==1
condition3 = rel_PE_df.index.time == exit_time_dt

rel_PE_df['PEhitstatus'] = ''
rel_PE_df.loc[condition1, 'PEhitstatus'] = 'SL_hit'
rel_PE_df.loc[condition2, 'PEhitstatus'] = 'TGThit'
rel_PE_df.loc[condition3, 'PEhitstatus'] = 'squareoff'

#modified PEhitstatus column
first_non_null = rel_PE_df[rel_PE_df['PEhitstatus'] != '']['PEhitstatus'].iloc[0]
rel_PE_df['PEhitstatus'] = np.where(rel_PE_df['PEhitstatus'] != '', first_non_null,'')

#--->Calcuating PEexitPrice column
rel_PE_df['PEexitPrice'] = np.NaN

rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'SL_hit','PEexitPrice'] = rel_PE_df['PEstoploss']
rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'TGThit','PEexitPrice'] = rel_PE_df['PEtarget']
rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'squareoff','PEexitPrice'] = rel_PE_df['PEclose']

# ------------> to get any one of hit only not all

#--->Calcuating PE_MTM column
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_MTM'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PEclose'], np.nan)

#--->Calcuating PE_highMTM (entryPrice-low)
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_highMTM'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PElow'], np.nan)

#--->Calcuating PE_maxMTM
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)

rel_PE_df['PE_maxMTM'] = np.where(condition,np.where(rel_PE_df['PE_highMTM'].cummax() > 0 ,rel_PE_df['PE_highMTM'].cummax() ,np.nan),np.nan)


#--->Calcuating PE_lowMTM  (entryPrice-high)
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_lowMTM'] = np.where(condition,rel_PE_df['PEentryPrice'] - rel_PE_df['PEhigh'], np.nan)

#--->Calcuating PE_minMTM
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_minMTM'] = np.where(condition,rel_PE_df['PE_lowMTM'].cummin(), np.nan)



#--->Calcuating PE_PnL column
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_PnL'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PEexitPrice'], np.nan)
#merging dataframes merged_df,rel_CE_df and rel_PE_df and make final_df


#NOte --> name changed to index
merged_df.reset_index(inplace=True)
rel_CE_df.reset_index(inplace=True)
rel_PE_df.reset_index(inplace=True)


dff1 = pd.merge(merged_df,rel_CE_df,left_on='datetime', right_on='index' )

combo_df = pd.merge(dff1,rel_PE_df, left_on='datetime', right_on='index')

combo_df['CBopen'] = combo_df['CEopen']  + combo_df['PEopen']
combo_df['CBhigh'] = np.maximum(combo_df['CEhigh'] + combo_df['PElow'],combo_df['CElow'] + combo_df['PEhigh'])
combo_df['CBlow'] = np.minimum(combo_df['CEhigh'] + combo_df['PElow'],combo_df['CElow'] + combo_df['PEhigh'])

combo_df['CBclose'] = combo_df['CEclose']  + combo_df['PEclose']
columns_needs_ffill = combo_df.columns[~combo_df.columns.isin(['CE_PnL','PE_PnL'])]
combo_df[columns_needs_ffill] = combo_df[columns_needs_ffill].fillna(method='ffill')

# print(combo_df[['CE_PnL','PE_PnL']])
# combo_df.to_csv('kebro.csv', index=False)

combo_df

combo_df.to_csv('combodf_18_03_2021')  


# #------------------------------PART 3------------------------------------------------------------------------
# # getting last row close values 
# final_close = df['close'][df['close'].last_valid_index()]


# #status remains
# # final_CEhitstatus = df['CEhitstatus'][df['CEhitstatus'].last_valid_index()]       # not working
# x_ser = df['CEhitstatus'][df['CEhitstatus'].values !='']
# final_CEhitstatus = x_ser[x_ser.last_valid_index()]

# final_CEentryPrice = df['CEentryPrice'][df['CEentryPrice'].last_valid_index()]
# final_CE_maxMTM = df['CE_maxMTM'][df['CE_maxMTM'].last_valid_index()]
# final_CE_minMTM = df['CE_minMTM'][df['CE_minMTM'].last_valid_index()]
# final_CE_PnL = df['CE_PnL'][df['CE_PnL'].last_valid_index()]


# final_PEentryPrice = df['PEentryPrice'][df['PEentryPrice'].last_valid_index()]
# final_PEhitstatus = df['PEhitstatus'][df['PEhitstatus'].last_valid_index()]
# final_PE_maxMTM = df['PE_maxMTM'][df['PE_maxMTM'].last_valid_index()]
# final_PE_minMTM = df['PE_minMTM'][df['PE_minMTM'].last_valid_index()]
# final_PE_PnL = df['PE_PnL'][df['PE_PnL'].last_valid_index()]

# finalTotal_PnL = final_CE_PnL + final_PE_PnL

# data = {
#     'final_close'       :   [df['close'] [df['close'].last_valid_index()] ],
#     'final_CEentryPrice':   [df['CEentryPrice'][df['CEentryPrice'].last_valid_index()]],
#     'final_CEhitstatus':    [x_ser[x_ser.last_valid_index()]],
#     'final_CE_maxMTM':      [df['CE_maxMTM'][df['CE_maxMTM'].last_valid_index()]],
#     'final_CE_minMTM':      [df['CE_minMTM'][df['CE_minMTM'].last_valid_index()]],
#     'final_CE_PnL':         [df['CE_PnL'][df['CE_PnL'].last_valid_index()]],
# 'final_PEentryPrice':       [df['PEentryPrice'][df['PEentryPrice'].last_valid_index()]],
# 'final_PEhitstatus':        [df['PEhitstatus'][df['PEhitstatus'].last_valid_index()]],
#     'final_PE_maxMTM':      [df['PE_maxMTM'][df['PE_maxMTM'].last_valid_index()]],
#     'final_PE_minMTM':      [df['PE_minMTM'][df['PE_minMTM'].last_valid_index()]],
#     'final_PE_PnL':         [df['PE_PnL'][df['PE_PnL'].last_valid_index()]],
#     'finalTotal_PnL' :      finalTotal_PnL
# }

# result_df = pd.DataFrame(data)

# print(result_df)


