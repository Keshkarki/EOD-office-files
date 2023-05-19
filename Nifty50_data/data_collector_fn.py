
import numpy as np
import pandas as pd
import yfinance as yf

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)

def downloading_files(start_date,end_date):
    #reading symbol-df file
    symbol_df = pd.read_csv('https://raw.githubusercontent.com/Keshkarki/rough-file/master/symbol.csv',header=None).squeeze()
    # print(symbol_df)

    #All nse equities 
    equity_details = pd.read_csv('https://raw.githubusercontent.com/Keshkarki/rough-file/master/EQUITY_L.csv')['SYMBOL']
    # print(equity_details)

    equity_50 = equity_details[equity_details.isin(symbol_df)]
    # print(equity_50)
    print(len(equity_50))


    """downloading all files one by one"""
    # #change limit no of files out of 50 we need ----->
    # for name in equity_50[ :2 ]:
    #     data = yf.download(f"{name}.NS", start_date, end_date)
    #     data['Symbol'] = name  #adding new column with symbol 

    #     #downloading folder 
    #     data.to_csv(f"C:\\Users\\Admin\\OneDrive\\Desktop\\Nifty50_data\\Data3\\{name}.NS.csv")


    """combinning files"""
    data_list = []

    start_date = pd.Timestamp.now() - pd.Timedelta(days=365*10)
    end_date = pd.Timestamp.now()

    for name in equity_50[0:2]:
        data = yf.download(tickers=F"{name}.NS",start=start_date, end=end_date)
        data['Symbol'] = name
        data_list.append(data)

    combined_data = pd.concat(data_list)

    """manuplulating file"""
    combined_data['daily_return'] = (((combined_data['Adj Close'] - combined_data['Adj Close'].shift(1)) / combined_data['Adj Close'].shift(1))*100).fillna(method='bfill')
    combined_data.insert(0,'day',combined_data.index.day.to_list())


            # Resample daily data to monthly data
    # Resample daily data to monthly data
    monthly_data = combined_data.resample('BM').last()

    # Calculate monthly returns
    monthly_data['monthly_return'] = ((monthly_data['Adj Close'] - monthly_data['Adj Close'].shift(1)) / monthly_data['Adj Close'].shift(1))*100

    # Drop the first row as it will have NaN value
    monthly_data = monthly_data.dropna()

    # Print the monthly returns
    # print(monthly_data['monthly_return'])


    merged_data = combined_data.reset_index()
    monthly_data = monthly_data.reset_index()


    merged_data = combined_data.merge(monthly_data[['Date', 'monthly_return']], how='left', on='Date')
    merged_data['monthly_return'] = merged_data['monthly_return'].fillna(0)
    merged_data = merged_data.set_index('Date')

        ###PART 2 index data ###
    index_df = yf.download('^NSEI',start=start_date, end=end_date)
    index_df['Symbol'] = 'index'

    index_df['daily_return'] = (((index_df['Adj Close'] - index_df['Adj Close'].shift(1))/index_df['Adj Close'].shift(1))*100).fillna(method='bfill')
    index_df.insert(0,'day',index_df.index.day.to_list())
    index_df

        # Resample daily data to monthly data
    monthly_data2 = index_df.resample('BM').last()

    # Calculate monthly returns
    monthly_data2['monthly_return'] = ((monthly_data2['Adj Close'] - monthly_data2['Adj Close'].shift(1)) / monthly_data2['Adj Close'].shift(1))*100

    # Drop the first row as it will have NaN value
    monthly_data2 = monthly_data2.dropna()

    # Print the monthly returns
    # print(monthly_data2['monthly_return'])


    index_df = index_df.reset_index()
    monthly_data2 = monthly_data2.reset_index()

    index_df = index_df.merge(monthly_data2[['Date', 'monthly_return']], how='left', on='Date')
    index_df['monthly_return'] = index_df['monthly_return'].fillna(0)

    index_df = index_df.set_index('Date')


## PART4- merging stock_df with index_df

    merged_data = merged_data.reset_index()
    index_df = index_df.reset_index()

    merged_df = merged_data.merge(index_df[['Symbol', 'Date', 'daily_return', 'monthly_return']], on=['Date'], how='left')
    merged_df.fillna({'monthly_return': 0})

    merged_df = merged_df.set_index('Date').iloc[1:]

    merged_df.rename(columns={
    'Symbol_x' : 'symbol_stock',
    'daily_return_x' : 'daily_return_stock '	,
    'monthly_return_x' : 'monthly_return_stock',
    'Symbol_y'  : 'Symbol_index',
    'daily_return_y' : "daily_return_index",
    'monthly_return_y' : 'daily_return_index'
},inplace=True)
    
    return merged_df.head(200)


    merged_df.to_csv('merged_file.csv')
print(downloading_files(start_date='2012-01-01',end_date='2023-05-01'))