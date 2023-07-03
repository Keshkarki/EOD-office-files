
#%% NOte:
# Making master file second time for common stocks for all years 2018-2023
# also downloading outstanding shres for all stocks
# RELIANCE OUTSTANDING SHARE - 6729321244
# outstanding sheet data on second sheet of common ticker excel



#%% imprting lib
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import timedelta
pd.set_option('display.max_columns', None)


#%% all common tickers in 5 years 2018-2023
ticker_list = pd.read_excel("C:\keshav\historicalData2013-2023\PART2_common_stocks\common_ticker_exel.xlsx",sheet_name= 'common_tickers18-23', header=None).squeeze().to_list()
ticker_list

#%% ## downloading 5 years data from 2018-2023 for all tickers in ticker_list

start_date = '2018-01-01'
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


#%% DOWNLOADING OUTSTANDING SHARES
#single
# yf.Ticker('TCS.NS').info.get('sharesOutstanding')

outstandingShares = []
for ticker in ticker_list:
    os = yf.Ticker(ticker).info.get('sharesOutstanding')
    outstandingShares.append(os)


#%% making series got all outstanding shares for all the tickers
my_ser = pd.Series(outstandingShares, index=ticker_list)
my_ser.to_excel('outstandingSharesDownloades.xlsx')