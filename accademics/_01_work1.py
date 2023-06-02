
#   %% READING DATA AND FORMATIING 
import numpy as np
import pandas as pd

df = pd.read_csv("Nifty50.csv")
df

df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date',inplace=True)

df = df[['Open', 'High', 'Low', 'Close']]
df

# Calculate the daily returns by dividing the current day's close price by the previous day's close price and subtracting 1. You can use the shift() function to get the previous day's close price:
df['Daily_Return'] = round(df['Close'] / df['Close'].shift(1) - 1,2)
df['Daily_Return']

#since first in NaN
df = df.iloc[1:, : ]
df

df['Daily_Return'] = df['Close'] / df['Close'].shift(1) - 1
