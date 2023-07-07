
#%% NOTE:
# 1. buy ==1,
# 2. sell ==0 




#%% 
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go




#%%
nifty = yf.download('^NSEI')['Adj Close']

#%%
cum_max = nifty.cummax()
nifty = nifty.to_frame(name='price')  #Converted to dataframe first
nifty['cum_max'] = cum_max


drawdown = (nifty['price'] - nifty['cum_max'])/nifty['cum_max']*100
nifty['drawdown'] = drawdown
nifty = round(nifty,2)



#%%
#   trace
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



#%%
nifty['cum_min'] =  nifty['price'].cummin()

bounce_up = (nifty['price'] - nifty['cum_min'])/nifty['cum_min']*100
nifty['bounce_up'] = bounce_up
nifty = round(nifty,2)



#%%
nifty['entry'] = np.where(nifty['bounce_up'] > buy_bounce, 1,0)  # buy = 1
nifty['exit']   = np.where(nifty['drawdown'] < - (sell_drawdown), 1,0)   # sell  =1



#%% calculating entry price
nifty['position'] = 1

#%%
# =+IF(E6=1,IF(G7="Sell",0,E6),IF(F7="Buy",1,E6))

for i in range(len(nifty)):
    nifty['position'] = np.where(nifty['position'].shift() ==1, 
                        np.where(nifty['exit'] ==1, 0, nifty['position'].shift()),
                        np.where(nifty['entry'] ==1,1,nifty['position'].shift() ))

nifty = nifty.iloc[2:].copy()
nifty['position'] = nifty['position'].astype(int)



#%% entry price


nifty['entry_price'] = 0

for i in range(len(nifty)):
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



#%%
nifty['PnL'] = np.where(nifty['exit_price'] !=0, nifty['exit_price']-nifty['entry_price'].shift(),0)


#%% pnl pct
nifty['PnL_pct'] = (nifty['PnL']/nifty['entry_price'].shift())*100