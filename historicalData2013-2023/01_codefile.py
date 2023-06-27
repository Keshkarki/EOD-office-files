
"""Notes:
            1. master file is keep updating "C:\keshav\50stocks_performance\masterFile.csv" from this path
            2.will required two file master df and symbol from nifty50.csv

"""

#   %%(1) importing lib and file reading 
import numpy as np
import pandas as pd
import datetime as dt


masterDf = pd.read_csv("C:\\keshav\\50stocks_performance\\masterFile.csv", parse_dates=['Date'],index_col='Date')


niftyDf = pd.read_csv("C:\\keshav\\historicalData2013-2023\\Nifty50.csv",usecols=['symbol','Outstanding shares'])

niftyDf.set_index('symbol',inplace=True)

#adding price for given date in niftyDf
niftyDf.insert(0,'price',np.nan)





# %% for 2012
mainDf ={}
yearly = ['2012', '2013','2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']

for date in yearly:
    startDate = f"{date}-03-31"  
    startDateDt = pd.to_datetime(startDate)

    # Create a new DataFrame for each iteration
    df = niftyDf.copy()


    for company in niftyDf.index:
        try:
            if startDateDt in masterDf.index:
                datePresent = startDateDt
                value = masterDf[company].loc[datePresent]
                df.loc[company,'price'] = value
            
            else:
                dateClosest = masterDf[masterDf.index<startDateDt].iloc[-1].name
                value = masterDf[company].loc[dateClosest]
                df.loc[company,'price'] = value

        except:
            print('Hello')
            df.loc[company, 'price'] = np.NaN

    #calculating mcap
        df['mCap'] = (df['price']*df['Outstanding shares'])/10000000

        mainDf[f"{date}"] = df

# %%  we can filter top 10 by mCap
mainDf['2012'].sort_values(by='mCap', ascending=False).head(10)
mainDf['2013'].sort_values(by='mCap', ascending=False).head(10)



# %%
#capturing next year price for top 10 stocks by mCap

yearly2 = ['2012', '2013','2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']

result_dict = {}

for year in yearly2:
    top_year = mainDf[year].sort_values(by='mCap', ascending=False).head(10)
    next_year = str(int(year) + 1)  # Assuming the next year is the current year + 1
    merged_df = pd.merge(top_year, mainDf[next_year], left_index=True, right_index=True, suffixes=(year, next_year))[[f'price{year}',f'price{next_year}']]
    merged_df['return'] = (merged_df[f'price{next_year}'] / merged_df[f'price{year}']) * 100 - 100
    result_dict[year] = merged_df

# Accessing the result for a specific year
print(result_dict['2012'])


# %% making empty final_df

data = {'year': ['2012-2013', '2013-2014', '2014-2015', '2015-2016', '2016-2017', '2017-2018',
                 '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023']}

finalDf = pd.DataFrame(data)
finalDf['avgReturn'] = np.nan
finalDf['niftyReturn'] = np.nan
finalDf.set_index('year', inplace=True)
finalDf


#   %%avg returns
for year in yearly2:
    finalDf.loc[f"{year}-{str(int(year)+1)}", 'avgReturn'] =  np.average(result_dict[year]['return'])



# %% creating emtpynifty dataframe



data2 = {'year': ['2012', '2013','2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'],
    }

niftyTable = pd.DataFrame(data2)
niftyTable['price'] = np.nan
niftyTable.set_index('year', inplace=True)

print(niftyTable)



# %% capturing price for nifty

yearly = ['2012', '2013','2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']

for date in yearly:
    startDate = f"{date}-03-31"  
    startDateDt = pd.to_datetime(startDate)

    try:
        if startDateDt in masterDf.index:
            datePresent = startDateDt
            value = masterDf['Nifty'].loc[datePresent]
            niftyTable.loc[date,'price'] =  value
        
        else:
            dateClosest = masterDf[masterDf.index<startDateDt].iloc[-1].name
            value = masterDf['Nifty'].loc[dateClosest]
            niftyTable.loc[date,'price'] =  value

    except:
        print('Hello')
        niftyTable.loc['Nifty', 'price'] = np.NaN




niftyTable['nextYearprice'] = niftyTable['price'].shift(-1)
niftyTable['return'] = (niftyTable['nextYearprice'] / niftyTable['price'])*100 -100
niftyTable =niftyTable.iloc[0:-1,:]
niftyTable.insert(0,'dateRange',['2012-2013', '2013-2014', '2014-2015', '2015-2016', '2016-2017', '2017-2018',
                 '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023'])
niftyTable.set_index('dateRange', inplace=True)
niftyTable
# %%
finalDf2 = pd.merge(finalDf,niftyTable, left_index=True, right_index=True)[['avgReturn','return']]
finalDf2['diff'] = finalDf2['avgReturn'] - finalDf2['return']