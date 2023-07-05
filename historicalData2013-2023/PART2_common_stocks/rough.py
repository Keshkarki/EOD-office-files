
# %% Notes -->
# 1. creating bins first and then runnig loop second method
# 2. nifty taking every year 5o stocks

#%% importing libraries
import numpy as np
import pandas as pd
import datetime as dt
import warnings

pd.set_option('display.width', 1000)
warnings.simplefilter(action='ignore', category=FutureWarning)
# pd.set_option('display.max_rows',None)




#%% reading file
master_df = pd.read_csv("C:\\keshav\\50stocks_performance\\master_file2.csv", parse_dates=['Date'],dayfirst=True , index_col='Date')

#reading Beta1 sheet of excel file
beta_file = pd.read_excel("C:\\keshav\\historicalData2013-2023\\Beta_nifty.xlsx",sheet_name='Beta1', header=1, parse_dates=['Date'], index_col='Date')
beta_file = beta_file.round(1)

#common ticker file
nifty_df = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\common_ticker_exel.xlsx", sheet_name='outstanding_shares', usecols=['all_companies', 'Outstanding shares'], index_col='all_companies')


stocks_2018 = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2018').squeeze()

stocks_2019 = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2019').squeeze()

stocks_2020 = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2020').squeeze()

stocks_2021 = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2021').squeeze()
stocks_2022= pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2022').squeeze()

stocks_2023 = pd.read_excel("C:\\keshav\\historicalData2013-2023\\PART2_common_stocks\\2013_2018_50Stocks.xlsx",sheet_name='2023').squeeze()



#%% INPUT DATES
start_date_input = pd.to_datetime("2018-03-31")
end_date_input = pd.to_datetime("2023-03-31")
filter_mode = input("choose filter  mode ['market_cap, 'beta'] : ")
beta_value = 0.7

period = input(f"Please choose from [yearly,quarterly, monthly, custom]  : ")

if period == "custom":
    input_custom_days = int(input('Please choose custom days : '))

else:
    input_custom_days = 30 

#DATES WHICH IS PRESENT IN master_df
start_date = master_df[master_df.index <= start_date_input].index.max()
end_date = master_df[master_df.index <= end_date_input].index.max()


#%% filtered daily
filtered_daily = [i for i in master_df.index]
 

#%% MAKING BINS --> annual, quarterly, monthly, custom
filtered_yearly = []
for year in range(start_date.year, end_date.year + 1):
    # Create a timestamp for March 31 of the current year
    target_date = pd.Timestamp(year=year, month=3, day=31)
    closest_date = master_df.index[master_df.index <= target_date].max()
    filtered_yearly.append(closest_date)



# %% Monthly filtered df
monthly_dates = pd.date_range(start=start_date, end=end_date, freq='M')
filtered_monthly = []

# Iterate over each monthly date
for date in monthly_dates:
    closest_date = master_df.index[master_df.index <= date].max()
    filtered_monthly.append(closest_date)


#%% Qurterly 
quarterly_dates = pd.date_range(start=start_date, end=end_date, freq='Q')
filtered_quarterly = []

# Iterate over each quarterly date
for date in quarterly_dates:
    closest_date = master_df.index[master_df.index <= date].max()
    filtered_quarterly.append(closest_date)


#%% custom dates 
custom_dates = pd.date_range(start=start_date, end=end_date, freq=f"{input_custom_days}D")
filtered_custom = []

# Iterate over each custom date
for date in custom_dates:
    closest_date = master_df.index[master_df.index <= date].max()
    filtered_custom.append(closest_date)


#%%  #MAKING  filtered_dates single function for all variables

if period == 'yearly':
    filtered_dates = filtered_yearly

elif period == 'monthly':
    filtered_dates = filtered_monthly

elif period == 'quarterly':
    filtered_dates = filtered_quarterly

elif period == 'custom':
    filtered_dates = filtered_custom


# betadates fitered
try:
    beta_file_filtered = beta_file.loc[filtered_dates]

except:
    pass


#%% ========================= LOOP PART CAPTURING DETAILS AND INSERTING IN DICTIONARIES ==============================
main_dict = {}
nifty_dict = {}
capital = 100000000
no_of_stocks = 5
portfolio = pd.DataFrame(columns  = ['Date', 'portfolio_values'])

for i in range(len(filtered_dates)):
    print(filtered_dates[i])
    try:
        
        if filtered_dates[i].year == 2018:
            df = stocks_2018

        if filtered_dates[i].year == 2019:
            df = stocks_2019

        if filtered_dates[i].year == 2020:
            df = stocks_2020

        if filtered_dates[i].year == 2021:
            df = stocks_2021

        if filtered_dates[i].year ==2022:
            df = stocks_2022

        if filtered_dates[i].year == 2023:
            df = stocks_2023
            
        df = nifty_df.copy()

        for company in df.index:
            value = master_df.loc[filtered_dates[i],company]
            df.loc[company,'price'] = value
            
            #for next year
            value2 = master_df.loc[filtered_dates[i+1], company]
            df.loc[company,'next_year_price'] = value2
            

        if filter_mode == "beta":
    #----- for filtering based on below criteria
            # mask = beta_file_filtered.loc[filtered_dates[i]] < 0.7
            # filtered_row = beta_file_filtered.loc[filtered_dates[i]][mask]

    #----for filtering top10 lowest beta
            filtered_row = beta_file_filtered.loc[filtered_dates[i]]
            filtered_row = filtered_row.sort_values().head(no_of_stocks)
            df = df[df.index.isin(filtered_row.index)]
            df_companies = df.index

            #DATES BETWEEN MONTH --------------------
            daily_dates_between = [timestamp for timestamp in filtered_daily if filtered_dates[i] <= timestamp < filtered_dates[i+1]]

            for j in range(len(daily_dates_between)):
                # print(daily_dates_between[j])

                if daily_dates_between[j] == filtered_dates[i]:
                    
                    df['capital'] = capital/len(df_companies)
                    df['no_of_shares'] = df['capital']/df['price']
                    df['invested'] = df['no_of_shares']*df['price']
                    # print(df)

                df2 = nifty_df.loc[df_companies]
                # print(df2)

                for company in df.index:
                    value = master_df.loc[daily_dates_between[j],company]
                    df2.loc[company,'price'] = value
                    
                    #for next year
                    try:
                        value2 = master_df.loc[daily_dates_between[j+1], company]
                        df2.loc[company,'next_year_price'] = value2
                    except:
                        pass

                    df2['market_cap'] = df2['Outstanding shares']*df2['price']
                    df2 = df2.sort_values(by='market_cap', ascending=False).head(no_of_stocks)  #top 10

                    df2['no_of_shares'] = df['no_of_shares']
                    df2['invested'] = df2['no_of_shares']*df2['price']

                date = daily_dates_between[j]
                capital = round(df2['invested'].sum())

                # print(date,capital)

                portfolio = portfolio.append({'Date': date, 'portfolio_values': capital}, ignore_index=True)

        if filter_mode == 'market_cap':
            df['market_cap'] = df['Outstanding shares']*df['price']
            df = df.sort_values(by='market_cap', ascending=False).head(no_of_stocks)  #top 10
            df_companies = df.index

            # portfolio calculation
            # df['capital'] = capital
            # df['no_of_shares'] = df['capital']/df['price']
            # df['invested'] = df['no_of_shares']*df['price']
            # print(df)

        #DATES BETWEEN MONTH --------------------
            daily_dates_between = [timestamp for timestamp in filtered_daily if filtered_dates[i] <= timestamp < filtered_dates[i+1]]

            for j in range(len(daily_dates_between)):
                # print(daily_dates_between[j])

                if daily_dates_between[j] == filtered_dates[i]:
                    
                    df['capital'] = capital/len(df_companies)
                    df['no_of_shares'] = df['capital']/df['price']
                    df['invested'] = df['no_of_shares']*df['price']
                    # print(df)

                df2 = nifty_df.loc[df_companies]
                # print(df2)

                for company in df.index:
                    value = master_df.loc[daily_dates_between[j],company]
                    df2.loc[company,'price'] = value
                    
                    #for next year
                    try:
                        value2 = master_df.loc[daily_dates_between[j+1], company]
                        df2.loc[company,'next_year_price'] = value2
                    except:
                        pass

                    df2['market_cap'] = df2['Outstanding shares']*df2['price']
                    df2 = df2.sort_values(by='market_cap', ascending=False).head(no_of_stocks)  #top 10

                    df2['no_of_shares'] = df['no_of_shares']
                    df2['invested'] = df2['no_of_shares']*df2['price']

                date = daily_dates_between[j]
                capital = round(df2['invested'].sum())

                # print(date,capital)

                portfolio = portfolio.append({'Date': date, 'portfolio_values': capital}, ignore_index=True)
                # # print(df2)

        df['return'] = df['next_year_price']/df['price']*100 -100
        df = df['return'].mean()
        main_dict[filtered_dates[i]] = df

        #also for nifty
        #creating every time within loop
        nifty_temp_df = pd.DataFrame(index=['Nifty'], columns=['price', 'next_year_price'])
        value_nifty = master_df.loc[filtered_dates[i],'Nifty']
        nifty_temp_df.loc['Nifty','price'] = value_nifty    

        #for next year        
        value2_nifty = master_df.loc[filtered_dates[i+1], 'Nifty']
        nifty_temp_df.loc['Nifty','next_year_price'] = value2_nifty

        nifty_temp_df['return'] = nifty_temp_df['next_year_price']/nifty_temp_df['price']*100 -100
        nifty_temp_df = nifty_temp_df['return'].values[0]
        nifty_dict[filtered_dates[i]] = nifty_temp_df

    except:
        pass

    if i == 3:
        break

print(portfolio)

#%% PRINT PORTFOLIO
# portfolio.to_csv('portfolio33.csv')


#%% # Assuming the dictionary with returns is stored in the variable 'returns_dict'
returns_df1 = pd.DataFrame.from_dict(main_dict, orient='index', columns=['top10_stocks_avg_returns'])
returns_df2 = pd.DataFrame.from_dict(nifty_dict, orient='index', columns=['nifty_returns'])
final_df = pd.merge(returns_df1,returns_df2, left_index=True, right_index=True)
final_df['diff'] = final_df['top10_stocks_avg_returns'] - final_df['nifty_returns']
final_df = final_df.round(1)
print(final_df)


