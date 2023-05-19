import numpy as np
import pandas as pd
import datetime as dt
import re


#all columns
# pd.set_option('display.max_columns',None)

def three_years_pnl():
    """READING FILES"""
    df_21 = pd.read_csv("C:\\keshav\\5year_monthly_data\\fy20-21.csv")
    df_21 = df_21.iloc[1:]
    print(df_21.head())

    df_22 = pd.read_csv("C:\\keshav\\5year_monthly_data\\fy21-22.csv")
    df_22 = df_22.iloc[1:]
    # print(df_22.head())

    df_23 = pd.read_csv("C:\\keshav\\5year_monthly_data\\fy22-23.csv")
    print(df_23.head())    



    """"SETTING df_23 --> temp_df"""
    df_23.drop(columns=['ISIN','BuyQty','BuyRate','BuyVal','SellQty','SellRate','SellVal','LTPRate','LTPVal','IncomeTax'],inplace=True)
    print(df_23.head())    

    column_names = ['Instrument', 'SoldQuantity', 'BuyAvg', 'BuyValue', 'SellAvg', 'SellValue', 'NetRealizedPnL', 'RealisedGLPerc', 'CloseQuantityAsOnLastDay', 'BuyAvgOpenPrice', 'SellAvgPrice', 'CMP', 'NetUnrealizedPnL', 'NetUnrealizedPnlPerc', 'TotalGL', 'TotalGLPerc', 'DayGL', 'DayGLPerc', 'AssetType']

    temp_df = pd.DataFrame(columns=column_names)
    temp_df['Instrument'] = df_23['ScriptName'].values
    temp_df['NetRealizedPnL'] = df_23['NetRealizedPnL'].values
    temp_df.fillna(0,inplace=True)
    print(temp_df)


    """Extracting date out of temp_df and making it index column"""
    temp_df['Date'] = pd.to_datetime(temp_df['Instrument'].apply(lambda x: re.search(r'\d{2}[A-Za-z]{3}\d{4}', x).group(0)))
    temp_df.set_index('Date',inplace=True)
    print(temp_df.head())

    #same dimension we can concatenate just need to set date for above two dataframes
    print(df_21.shape)
    print(df_22.shape)
    print(temp_df.shape)


    df = pd.concat([df_21,df_22], axis=0)
    print(df.head())
    df['Date'] = df['Instrument'].str.extract(r'(\d{2}[A-Za-z]{3}\d{4})')
    df["Date"] = pd.to_datetime(df['Date'])
    df.set_index('Date',inplace=True)
    print(df.head())



    """Concatenate these two dataframe """
    merged_df = pd.concat([df,temp_df], axis=0).sort_index()
    merged_df.insert(0,"Year",merged_df.index.year.to_list())
    merged_df.insert(1,"Month",merged_df.index.month.to_list())
    print(merged_df)



    print("total of NetRealizedPnL   :" ,merged_df['NetRealizedPnL'].sum())
    print(round(merged_df.groupby(['Year','Month'])['NetRealizedPnL'].sum()))

print(three_years_pnl())





# def nifty():
#     nifty = pd.read_csv('Nifty50.csv')
#     print(nifty.head())

#     nifty['Date'] = pd.to_datetime(nifty['Date'])
#     nifty.set_index('Date',inplace=True)

#     nifty.loc[merged_df.index[0]:merged_df.index[-1]]



# print(nifty())