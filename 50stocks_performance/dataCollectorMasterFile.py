#Code for updating masterfile daily

# %%
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import timedelta
import datetime as dt
pd.set_option('display.max_columns', None)



# %%
## tickers
series = pd.read_csv('C:\\keshav\\50stocks_performance\\symbol.csv', header=None).squeeze()
series = series.apply(lambda ticker : f"{ticker}.NS")
series.to_list()



# %%
## downloading 15 years data from 2008-2023 for all 50 tickers
start_date = '2008-01-01'

today = dt.date.today()
today = today.strftime("%Y-%m-%d")



# %% No needed in master file

## downloading all tickers as csv files
# for ticker in series:
#     tickerName = ticker.split(".")[0]
#     data = yf.download(ticker, start_date,today)
#     data.insert(0,'company',tickerName)
#     data.to_csv(f"C:\\keshav\\50stocks_performance\\15YrsNifty50Data\\{ticker}.csv")



# %%
## downloading file for nifty
nifty = yf.download('^NSEI',start_date, today)
# nifty.to_csv('Nifty2008-2023.csv')

nifty.insert(0,'company','Nifty')
nifty.reset_index(inplace=True)
nifty


# %% masterFile (appending all)

df = pd.DataFrame()
for ticker in series:
    tickerName = ticker.split(".")[0]
    data = yf.download(ticker, start_date,today)
    data.insert(0,'company',tickerName)
    df = pd.concat([df,data])
    
df.reset_index(inplace=True)
df


# %%
merged_df = pd.concat([nifty,df])
merged_df = merged_df.pivot_table(index='Date', columns='company', values=['Adj Close'])
merged_df = merged_df.droplevel(0, axis=1)
nfitycol = merged_df['Nifty']
nfitycol
merged_df.drop(columns=['Nifty'],inplace=True)
merged_df.insert(0,'Nifty',nfitycol)
merged_df

#   %% to csv
merged_df.to_csv('masterFile.csv')

