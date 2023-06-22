# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

pd.set_option('display.max_columns',None)
pd.options.mode.chained_assignment = None



# %% all variables
rollingAvg = 20
stoplossPerc = 0.5
stdMultiplier = 1



# %% nifty

niftySingle = pd.read_csv('niftySingle.csv')

# niftySingle.insert(0,'company', 'nifty')
niftySingle = niftySingle.iloc[:,:5]

suffix = 'nifty'
niftySingle = niftySingle.rename(columns={'Date':'date','Open': f'{suffix}Open', 'High':f"{suffix}High", 'Low': f"{suffix}Low", 'Close':f'{suffix}Close'
})

niftySingle['date'] = pd.to_datetime(niftySingle['date'])
niftySingle.set_index('date',inplace=True)
niftySingle




# %% all companies
# list_of_companies = os.listdir('C:\\keshav\\bollingerBand\\Nifty50_Data')
# list_of_companies

# list_of_companies[19]

# %%

list_of_companies= ['RELIANCE.NS.csv', 'HDFCBANK.NS.csv', 'ICICIBANK.NS.csv', 'INFY.NS.csv', 'HDFC.NS.csv', 'TCS.NS.csv', 'ITC.NS.csv', 'KOTAKBANK.NS.csv', 'LT.NS.csv', 'AXISBANK.NS.csv']
list_of_companies


# %% FOR LOOP all stocks PnLPercent

allStocks = []

for i in range(len(list_of_companies)):
        stockSingle = pd.read_csv(f'C:\\keshav\\bollingerBand\\Nifty50_Data\\{list_of_companies[i]}', usecols=['Date','Open',"High", "Low",'Close'])

        company_name = f"{list_of_companies[i].split('.')[0]}"

        stockSingle = stockSingle.rename(columns={'Date':'date','Open': f'{company_name}Open', 'High':f"{company_name}High", 'Low': f"{company_name}Low", 'Close':f'{company_name}Close'
        })

        stockSingle['date'] = pd.to_datetime(stockSingle['date'])
        stockSingle.set_index('date',inplace=True)

        mergedDf = niftySingle.merge(stockSingle,left_index=True, right_index=True)

        mergedDf['ratioOpen'] = mergedDf[f'{company_name}Open'] / mergedDf['niftyOpen']
        mergedDf['ratioHigh'] = mergedDf[f'{company_name}High'] / mergedDf['niftyHigh']
        mergedDf['ratioLow'] =  mergedDf[f'{company_name}Low'] / mergedDf['niftyLow']
        mergedDf['ratioClose'] = mergedDf[f'{company_name}Close'] / mergedDf['niftyClose']

        mergedDf['mean'] = mergedDf['ratioClose'].rolling(rollingAvg).mean()
        mergedDf['std'] = mergedDf['ratioClose'].rolling(rollingAvg).std()

        mergedDf[f"+{stdMultiplier}std"] = mergedDf['mean'] + stdMultiplier*mergedDf['std']
        mergedDf[f"-{stdMultiplier}std"] = mergedDf['mean'] - stdMultiplier*mergedDf['std']
        mergedDf.dropna(subset=['mean'], inplace=True)


        # calculating  bandTouch
        mask1 = mergedDf['ratioClose'] <= mergedDf['-1std']
        mask2 = mergedDf['ratioLow'] <= mergedDf['-1std']
        mask3 = mergedDf['ratioClose'] >= mergedDf['+1std']
        mask4 = mergedDf['ratioHigh'] >= mergedDf['+1std']

        mergedDf['bandTouch'] = np.where(mask1 | mask2,'Lower',
                                                        np.where(mask3 |  mask4, "Upper",None)
                                                )   


        #bandTouch1
        mergedDf['bandTouch1'] = mergedDf['bandTouch'].fillna(method='ffill')


        # closeLowerBand
        mergedDf['closeLowerBand'] = np.where(
                                        mergedDf['ratioClose'] >= mergedDf['-1std'],"Above","Below" 
                                                )
                


        #closeMidBand
        mergedDf['closeMidBand'] = np.where(
        mergedDf['ratioClose'] >= mergedDf['std'],
        "Above","Below" 
                )


        # closeUpperBand
        mergedDf['closeUpperBand'] = np.where(
        mergedDf['ratioClose'] >= mergedDf['+1std'],
        "Above","Below" 
                )


        #closeAboveBelow
        mask1 = pd.isna(mergedDf['bandTouch1'])
        mask2 = mergedDf['bandTouch1'] == 'Upper'
        mask3 = mergedDf['ratioClose'] <= mergedDf['+1std']
        mask4 = mergedDf['ratioClose'] >= mergedDf['-1std']

        mergedDf['closeAboveBelow'] = np.where(
                                                mask1,None,np.where(
                                                        mask2,
                                                                np.where(mask3,"Below", "Above" ),
                                                                np.where(mask4,"Above", "Below" ) )
                                                )


        #signal
        mergedDf['signal'] = None

        for i in range(mergedDf.shape[0]):
                if (mergedDf['bandTouch1'].iloc[i] == 'Upper') and (mergedDf['closeUpperBand'].iloc[i] == 'Below'):
                        mergedDf['signal'].iloc[i] = 'Sell'
                elif (mergedDf['bandTouch1'].iloc[i] == 'Lower') and (mergedDf['closeLowerBand'].iloc[i] == 'Above'):
                        mergedDf['signal'].iloc[i] = 'Buy'
                else:
                        mergedDf['signal'].iloc[i] = mergedDf['signal'].iloc[i-1]


        
        #entrySignal
        mergedDf['entrySignal'] = np.where(mergedDf['signal'] != mergedDf['signal'].shift(),mergedDf['signal'],None )


        #entryRatio
        mergedDf['entryRatio'] = np.nan
        for i in range(mergedDf.shape[0]):
                mergedDf['entryRatio'] = np.where(
                                                pd.notna(mergedDf['entrySignal']),
                                                mergedDf['ratioClose'],
                                                mergedDf['entryRatio'].shift()
                                                )

                mergedDf['entryRatio'] = mergedDf['entryRatio']


        #entryPrice
        mergedDf['entryPrice'] = np.nan
        for i in range(mergedDf.shape[0]):
                mergedDf['entryPrice'] = np.where(
                                                pd.notna(mergedDf['entrySignal']),
                                                mergedDf[f'{company_name}Close'],
                                                mergedDf['entryPrice'].shift()
                                                        )


        #stoploss
        mergedDf['stopLoss'] = np.nan
        for i in range(mergedDf.shape[0]):
                mergedDf['stopLoss'] = np.where(
                        pd.notna(mergedDf['entrySignal']),
                        stoplossPerc*mergedDf['std'],
                        mergedDf['stopLoss'].shift()

                )
      

        #stoplossRatio
        mergedDf['stopLossRatio'] = np.nan

        for i in range(mergedDf.shape[0]):
                mergedDf['stopLossRatio'] = np.where(
                                                        mergedDf['entrySignal'] == 'Buy',
                                                        mergedDf['entryRatio'] - mergedDf['stopLoss'],
                                                        np.where(
                                                                mergedDf['entrySignal'] == 'Sell',
                                                                mergedDf['entryRatio'] + mergedDf['stopLoss'],
                                                                mergedDf['stopLossRatio'].shift()

                                                        )

                        )


        # stopLossHit
        mergedDf['stopLossHit'] = None
        mask1 = pd.notna(mergedDf['entrySignal'])
        mask2 = mergedDf['signal'] == 'Buy'
        mask3 = mergedDf['ratioClose']<=mergedDf['stopLossRatio']
        mask4 = mergedDf['ratioClose'] >= mergedDf['stopLossRatio']

        for i in range(mergedDf.shape[0]):
                mergedDf['stopLossHit'] = np.where(mask1,"No", 
                                        np.where(mask2, np.where(mask3,"Yes",mergedDf['stopLossHit'].shift()), np.where(mask4,"Yes",mergedDf['stopLossHit'].shift()))

                )


        # targetRatio
        mergedDf['targetRatio'] = mergedDf['mean']



        #targetHit
        mergedDf['targetHit'] = None
        mask1 = pd.notna(mergedDf['entrySignal'])
        mask2 = mergedDf['signal'] == 'Buy'
        mask3 = mergedDf['ratioClose']>= mergedDf['targetRatio']
        mask4 = mergedDf['ratioClose'] <= mergedDf['targetRatio']

        for i in range(mergedDf.shape[0]):
                mergedDf['targetHit'] = np.where(mask1,"No", 
                                        np.where(mask2, np.where(mask3,"Yes",mergedDf['targetHit'].shift()), np.where(mask4,"Yes",mergedDf['targetHit'].shift()))

                )



        # tradeNo
        mergedDf['tradeNo'] = 0 
        for i in range(mergedDf.shape[0]):
                if pd.notna(mergedDf['entrySignal'].iloc[i]):
                        mergedDf['tradeNo'].iloc[i] = mergedDf['tradeNo'].iloc[i-1]+1
                else:
                        mergedDf['tradeNo'].iloc[i] = mergedDf['tradeNo'].iloc[i-1]
                

                mergedDf


        # exitSignal
        mergedDf['exitSignal'] = None

        mergedDf['exitSignal'] = np.where(pd.notna(mergedDf['entrySignal']), None,
                                        np.where(mergedDf['stopLossHit'] == 'Yes', 'SL_hit',
                                                np.where(mergedDf['targetHit'] == 'Yes', 'Tgt_hit', mergedDf['exitSignal'].shift())
                                                )
                                        )



        # exitPrice
        mask1 = pd.isna(mergedDf['exitSignal'].shift())
        mask2 = pd.notna(mergedDf['exitSignal'])
        mergedDf['exitPrice'] = np.where(mask1 & mask2,mergedDf[f'{company_name}Close'],np.nan )



        #PnL
        mergedDf['PnL'] = np.where(pd.notna(mergedDf['exitPrice']),
                                 np.where(mergedDf['signal'] == 'Buy', mergedDf['exitPrice'] - mergedDf['entryPrice'], mergedDf['entryPrice'] - mergedDf['exitPrice']),
                                 0
                                )


        # PnLPercent
        mergedDf['PnLPercent']= mergedDf['PnL']/mergedDf['entryPrice']*100
        filterdDf = mergedDf[(mergedDf['PnLPercent']!=0) & (pd.notna(mergedDf['PnLPercent']))]['PnLPercent']
        filterdDf =  filterdDf.reset_index().set_index('date')
        filterdDf['companyName'] = f'{company_name}'
        allStocks.append(filterdDf)




# **************************************************************************
# %% final result
final_result = pd.concat(allStocks)
final_result = pd.pivot_table(final_result, values='PnLPercent', index='date', columns='companyName')
final_result



# %% monthly profit

monthly_profit = final_result.resample('M').sum()
print(monthly_profit)



# %% yearly profit
# Define the start month and day of your financial year
financial_year_start_month = 4  # April
financial_year_start_day = 1    # 1st

# Define a function to determine the financial year based on the date
def get_financial_year(date):
    if date.month >= financial_year_start_month and date.day >= financial_year_start_day:
        return date.year + 1
    else:
        return date.year

# Apply the financial year function to the index to get the financial year
final_result['financial_year'] = final_result.index.map(get_financial_year)

# Calculate the annual profit by grouping by financial year and summing the profits
annual_profit = final_result.groupby('financial_year').sum()
annual_profit



# %% Adding average column
annual_profit['average'] = annual_profit.mean(axis=1)

