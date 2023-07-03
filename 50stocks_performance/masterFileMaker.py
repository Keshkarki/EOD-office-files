
#%% NOte:
# Making master file second time for common stocks for all years 2013-2023


#%% imprting lib
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import timedelta
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


#%% tickers generator
ticker_list = pd.read_excel("C:\\keshav\\50stocks_performance\\common_ticker_mf.xlsx", header=None).squeeze()
ticker_list



#%% ## downloading 10 years data from 2013-2023 for all tickers in ticker_list

start_date = '2013-01-01'
end_date = '2023-06-22'

dd = yf.download(ticker_list[0],start_date, end_date)
dd


#%% for all tickers and exporting csv 
# for ticker in ticker_list:
#     tickerName = ticker.split(".")[0]
#     data = yf.download(ticker, start_date,end_date)
#     data.insert(0,'company',tickerName)
#     data.to_csv(f"C:\\keshav\\50stocks_performance\\15YrsNifty50Data\\{ticker}.csv")


#%% downloading file for nifty
nifty = yf.download('^NSEI',start_date, end_date)
nifty.insert(0,'company','Nifty')
nifty.reset_index(inplace=True)
nifty

#%%
dd2 = yf.download(ticker_list[52],start_date, end_date)
dd2



#%% making masterfile apending all tickers at one file
df = pd.DataFrame()
for ticker in ticker_list:
    tickerName = ticker.split(".")[0]
    data = yf.download(ticker, start_date,end_date)
    data.insert(0,'company',tickerName)
    df = pd.concat([df,data])
    


#%% alteration on masterfile
df.reset_index(inplace=True)

merged_df = pd.concat([nifty,df])
merged_df = merged_df.pivot_table(index='Date', columns='company', values=['Adj Close'])
merged_df = merged_df.droplevel(0, axis=1)

nfitycol = merged_df['Nifty']

merged_df.drop(columns=['Nifty'],inplace=True)
merged_df.insert(0,'Nifty',nfitycol)
merged_df

#%%
merged_df.to_csv('master_file2.csv')