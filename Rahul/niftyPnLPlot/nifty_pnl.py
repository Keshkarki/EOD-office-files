
#%% note:
# 1. buy ==1,
# 2. sell ==0





#%% importing libraries
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go





#%% downloading nifty
nifty = yf.download('^NSEI')['Adj Close']

## calculated drawdown
cum_max = nifty.cummax()
nifty = nifty.to_frame(name='price')  #Converted to dataframe first
nifty['cum_max'] = cum_max

drawdown = (nifty['price'] - nifty['cum_max'])/nifty['cum_max']*100
nifty['drawdown'] = drawdown
nifty = round(nifty,2)


#%%
trace = go.Scatter(
    x = nifty.index,
    y = nifty['drawdown'],
    mode = 'lines',
    name = 'Line'
)
layout = go.Layout(
    title = 'Nifty price',
    xaxis = dict(title = 'Date'),
    yaxis = dict(title = 'Price')
)
# fig object by passing both
fig = go.Figure(data=[trace], layout= layout)
fig.show()




#%% INPUTS
sell_drawdown = 5  #5%
buy_bounce= 5      #5%


#%%  calculating bounce_up with cum_min
nifty['cum_min'] =  nifty['price'].cummin()

bounce_up = (nifty['price'] - nifty['cum_min'])/nifty['cum_min']*100
nifty['bounce_up'] = bounce_up
nifty = round(nifty,2)
nifty



## calculating entry and exit price
nifty['entry'] = np.where(nifty['bounce_up'] > buy_bounce, 1,0)  # buy = 1
nifty['exit']   = np.where(nifty['drawdown'] < - (sell_drawdown), 1,0)   # sell  =1



## position
nifty['position'] = 1
for i in range(len(nifty)):
    nifty['position'] = np.where(nifty['position'].shift() ==1,
                        np.where(nifty['exit'] ==1, 0, nifty['position'].shift()),
                        np.where(nifty['entry'] ==1,1,nifty['position'].shift() ))

nifty = nifty.iloc[2:].copy()
nifty['position'] = nifty['position'].astype(int)

## entry price
nifty['entry_price'] = nifty['price']
for i in range(1,len(nifty)): # skipping first
    if nifty['position'].iloc[i] == 1:
        if nifty['position'].shift().iloc[i] == 0:
            nifty['entry_price'].iloc[i] = nifty['price'].iloc[i]
        else:
            nifty['entry_price'].iloc[i] = nifty['entry_price'].shift().iloc[i]
    else:
        nifty['entry_price'].iloc[i] = 0



# %%  exit price
nifty['exit_price'] = 0
for i in range(len(nifty)):
    if (nifty['position'].shift().iloc[i] ==1) and (nifty['position'].iloc[i] ==0) :
        nifty['exit_price'].iloc[i] = nifty['price'].iloc[i]

    else:
        nifty['exit_price'].iloc[i] = 0

## PnL and Pnl_pct
nifty['PnL'] = np.where(nifty['exit_price'] !=0, nifty['exit_price']-nifty['entry_price'].shift(),0)
nifty['PnL_pct'] = (nifty['PnL']/nifty['entry_price'].shift())*100

df2 = nifty[['entry_price', 'exit_price', 'PnL', 'PnL_pct']]
df2
df2 = df2.reset_index()




#%% Create a new column 'captured_date' and initialize it with NaT
df2['rough'] = np.where(df2['entry_price'] == df2['entry_price'].shift(),0,1)
df2['Date'] = df2['Date'].astype(str)

df2['Date2'] = np.where(
    ((df2['rough'] == 1) & (df2['entry_price'] != 0)), df2['Date'],
    np.where((df2['rough'] == 1) & (df2['exit_price'] != 0), df2['Date'], 0)
)


#%%
df2['Date2'] = df2['Date2'].replace(0,None)
df2['Date2'] = df2['Date2'].fillna(method='ffill')
df2.drop('rough', axis=1,inplace=True)
df2


#%%
df2['Date2'] = df2['Date2'].shift()
df2['entry_price_shifted'] = df2['entry_price'].shift()

#%%
df2.rename(columns={'Date2': 'entry_date'}, inplace=True)
df2.rename(columns={'Date': 'exit_date'}, inplace=True)
#%%

df3 = df2[['entry_date', 'exit_date', 'entry_price_shifted','PnL', 'PnL_pct']]
df3 = df3[df3['PnL'] !=0]
