


# %% importing libraries **************************************************
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import timedelta
pd.set_option('display.max_columns', None)




# %% tickers ***************************************************
series = pd.read_csv('symbol.csv', header=None).squeeze()
series = series.apply(lambda ticker : f"{ticker}.NS")
series.to_list()



# %%  downloading 15 years data from 2008-2023 for all 50 tickers
start_date = '2008-01-01'
end_date = '2023-06-22'

dd = yf.download(series[0],start_date, end_date)
dd



# %%  downloading all tickers as csv files

# for ticker in series:
#     tickerName = ticker.split(".")[0]
#     data = yf.download(ticker, start_date,end_date)
#     data.insert(0,'company',tickerName)
#     data.to_csv(f"C:\\keshav\\50stocks_performance\\15YrsNifty50Data\\{ticker}.csv")





# %%  downloading file for nifty
nifty = yf.download('^NSEI',start_date, end_date)
nifty

# nifty.to_csv('Nifty2008-2023.csv')

# %%
nifty.insert(0,'company','Nifty')
nifty.reset_index(inplace=True)
nifty






# %%  appending all in one
df = pd.DataFrame()
for ticker in series:
    tickerName = ticker.split(".")[0]
    data = yf.download(ticker, start_date,end_date)
    data.insert(0,'company',tickerName)
    df = pd.concat([df,data])
    



# %%
df.reset_index(inplace=True)
df

# %%
nifty




# %%
merged_df = pd.concat([nifty,df])
merged_df




# %%
merged_df = merged_df.pivot_table(index='Date', columns='company', values=['Adj Close'])
merged_df = merged_df.droplevel(0, axis=1)
merged_df




# %%
nfitycol = merged_df['Nifty']
merged_df.drop(columns=['Nifty'],inplace=True)
merged_df.insert(0,'Nifty',nfitycol)
merged_df




# %%  PART 2 Analysis
companyLiist = merged_df.columns.to_list()

index_columns = companyLiist
empty_columns = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'ytd']

main_df = pd.DataFrame(index=index_columns, columns=empty_columns)
main_df


# %%
merged_df.index








# %%   input date
inputDate = "2015-01-12"
inputDateDt = pd.to_datetime(inputDate)


# CAlculating BASE DATES

if inputDateDt in merged_df.index:
    currentPriceList = merged_df.loc[inputDateDt]
else:
    print(f'{inputDateDt} not present in data take another date as current date')

# 1 day before     (daily)
dailyBaseDate =  inputDateDt - timedelta(days=1)

#   7 days before v (weekly)
weeklyBaseDate = inputDateDt - timedelta(days=7)

# 30 days before  (monthly)
monthlyBaseDate = inputDateDt - timedelta(days=30)


#90 days before (quarterly)
quarterlyBaseDate = inputDateDt - timedelta(days=90)

# 365 days before (yearly)
yearlyBaseDate = inputDateDt - timedelta(days=365)



## daily
if dailyBaseDate >= merged_df.index[0] and dailyBaseDate <= merged_df.index[-1]:  #if base date in range
    if dailyBaseDate in merged_df.index:                                             #if base date present directly
        basePriceList  = merged_df.loc[dailyBaseDate]
        dailyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'daily'] = dailyReturnPer


    else:
        temp_df = merged_df[merged_df.index < dailyBaseDate]  
        nearest_index = temp_df.index.searchsorted(inputDateDt)-1      #will get index
        date = temp_df.index[nearest_index]                                         #will get date 
        basePriceList = temp_df.loc[date]                                           #will get row or values
        dailyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'daily'] = dailyReturnPer
else:
    print('Date is out of range of dates')




## weekly
if weeklyBaseDate >= merged_df.index[0] and weeklyBaseDate <= merged_df.index[-1]:  #if base date in range
    if weeklyBaseDate in merged_df.index:                                             #if base date present directly
        basePriceList  = merged_df.loc[weeklyBaseDate]
        weeklyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'weekly'] = weeklyReturnPer


    else:
        temp_df = merged_df[merged_df.index < weeklyBaseDate]  
        nearest_index = temp_df.index.searchsorted(inputDateDt)-1      #will get index
        date = temp_df.index[nearest_index]                                         #will get date 
        basePriceList = temp_df.loc[date]                                           #will get row or values
        weeklyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'weekly'] = weeklyReturnPer
else:
    print('Date is out of range of dates')




## monthly
if monthlyBaseDate >= merged_df.index[0] and monthlyBaseDate <= merged_df.index[-1]:  #if base date in range
    if monthlyBaseDate in merged_df.index:                                             #if base date present directly
        basePriceList  = merged_df.loc[monthlyBaseDate]
        monthlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'monthly'] = monthlyReturnPer


    else:
        temp_df = merged_df[merged_df.index < monthlyBaseDate]  
        nearest_index = temp_df.index.searchsorted(inputDateDt)-1      #will get index
        date = temp_df.index[nearest_index]                                         #will get date 
        basePriceList = temp_df.loc[date]                                           #will get row or values
        monthlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'monthly'] = monthlyReturnPer
else:
    print('Date is out of range of dates')




## quarterly
if quarterlyBaseDate >= merged_df.index[0] and quarterlyBaseDate <= merged_df.index[-1]:  #if base date in range
    if quarterlyBaseDate in merged_df.index:                                             #if base date present directly
        basePriceList  = merged_df.loc[quarterlyBaseDate]
        quarterlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'quarterly'] = quarterlyReturnPer


    else:
        temp_df = merged_df[merged_df.index < quarterlyBaseDate]  
        nearest_index = temp_df.index.searchsorted(inputDateDt)-1      #will get index
        date = temp_df.index[nearest_index]                                         #will get date 
        basePriceList = temp_df.loc[date]                                           #will get row or values
        quarterlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'quarterly'] = quarterlyReturnPer
else:
    print('Date is out of range of dates')


## yearly
if yearlyBaseDate >= merged_df.index[0] and yearlyBaseDate <= merged_df.index[-1]:  #if base date in range
    if yearlyBaseDate in merged_df.index:                                             #if base date present directly
        basePriceList  = merged_df.loc[yearlyBaseDate]
        yearlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'yearly'] = yearlyReturnPer


    else:
        temp_df = merged_df[merged_df.index < yearlyBaseDate]  
        nearest_index = temp_df.index.searchsorted(inputDateDt)-1      #will get index
        date = temp_df.index[nearest_index]                                         #will get date 
        basePriceList = temp_df.loc[date]                                           #will get row or values
        yearlyReturnPer =  ((currentPriceList/basePriceList -1)*100).values
        main_df.loc[:,'yearly'] = yearlyReturnPer
else:
    print('Date is out of range of dates')

main_df




