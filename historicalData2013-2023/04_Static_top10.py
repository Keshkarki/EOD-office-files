
# %% Notes -->
# 1.static  yearly first top 10 stocks fixed as per first date

#%% importing libraries
import numpy as np
import pandas as pd
import datetime as dt
# pd.set_option('display.max_rows',None)


#%% reading file
master_df = pd.read_csv("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\historicalData2013-2023\\masterFile.csv", parse_dates=['Date'],index_col='Date')
nifty_df = pd.read_csv("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\historicalData2013-2023\\Nifty50.csv",usecols=['symbol','Outstanding shares'])
nifty_df.set_index('symbol',inplace=True)


#reading Beta1 sheet of excel file
beta_file = pd.read_excel("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\historicalData2013-2023\\Beta_nifty.xlsx",sheet_name='Beta1', header=1, parse_dates=['Date'], index_col='Date')
beta_file = beta_file.round(1)

#%% INPUT DATES
start_date_input = pd.to_datetime("2012-03-31")
end_date_input = pd.to_datetime("2023-03-31")
filter_mode = input("choose filter  mode ['market_cap, 'beta'] : ")
# filter_mode = "market_cap"  #"market_cap"  #beta
beta_value = 0.7


#temporary
# period = 'yearly'
# input_custom_days = 30

period = input(f"Please choose from [yearly,quarterly, monthly, custom]  : ")


if period == "custom":
    input_custom_days = int(input('Please choose custom days : '))

else:
    input_custom_days = 30 


#DATES WHICH IS PRESENT IN master_df
start_date = master_df[master_df.index <= start_date_input].index.max()
end_date = master_df[master_df.index <= end_date_input].index.max()
 

#%% MAKING BINS --> annual, quarterly, monthly, custom

filtered_yearly = []

# Iterate over each year from the start date until the end year
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
beta_file_filtered = beta_file.loc[filtered_dates]


#%% LOOP PART CAPTURING DETAILS AND INSERTING IN DICTIONARIES
main_dict = {}
nifty_dict = {}
first_bouquet  = [] 

filtered_dates_first = []

seen_years = set()
for timestamp in filtered_dates:
    year = timestamp.year
    if year not in seen_years:
        filtered_dates_first.append(timestamp)
        seen_years.add(year)


for i in range(0,len(filtered_dates)):
    # print(filtered_dates[i])
    try:
            
        df = nifty_df.copy()
        for company in df.index:
            value = master_df.loc[filtered_dates[i],company]
            df.loc[company,'price'] = value
            
            #for next year
            value2 = master_df.loc[filtered_dates[i+1], company]
            df.loc[company,'next_year_price'] = value2


        if filter_mode == "beta":
            if filtered_dates[i] in filtered_dates_first:
                mask = beta_file_filtered.loc[filtered_dates[i]] < 0.7
                filtered_row = beta_file_filtered.loc[filtered_dates[i]][mask]
                # print(filtered_row)
                df = df[df.index.isin(filtered_row.index)]
                first_bouquet = df.index.to_list()

            
            else:
                    # print(filtered_dates[i])
                    df = df[df.index.isin(first_bouquet)]
                    # print(filtered_dates[i])
                    # print(df)



        
        if filter_mode == 'market_cap':
                df['market_cap'] = df['Outstanding shares']*df['price']
                if filtered_dates[i] in filtered_dates_first:
                    # print(filtered_dates[i])
                    df = df.sort_values(by='market_cap', ascending=False).head(10)  #top 10
                    first_bouquet = df.index.to_list()

                else:
                    # print(filtered_dates[i])
                    df = df[df.index.isin(first_bouquet)]
                    # print(filtered_dates[i])
                    # print(df)



        df['return'] = df['next_year_price']/df['price']*100 -100
        df = df['return'].mean()
        main_dict[filtered_dates[i]] = df


        #also for nifty
        # creating every time within loop

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

    # if i==2:
    #     break


    

#%% # Assuming the dictionary with returns is stored in the variable 'returns_dict'
returns_df1 = pd.DataFrame.from_dict(main_dict, orient='index', columns=['top10_stocks_avg_returns'])
returns_df2 = pd.DataFrame.from_dict(nifty_dict, orient='index', columns=['nifty_returns'])
final_df = pd.merge(returns_df1,returns_df2, left_index=True, right_index=True)
final_df['diff'] = final_df['top10_stocks_avg_returns'] - final_df['nifty_returns']
final_df = final_df.round(1)
print(final_df)


# %%
