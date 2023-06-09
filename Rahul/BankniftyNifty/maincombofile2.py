import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta

pd.set_option('display.max_colwidth', None)

#variables
entryDaysFromExpiry = 0
exitDaysFromExpiry = 0
entryTime = '15:15'
exitTime = '15:15'
strikeDiff = 100                 
underlyingStrikeDiff = 50              

underlying = 'BANKNIFTY'
underlyingStrikeDiff = 100 if underlying == 'BANKNIFTY' else 50
OTM_points = 100

#Part1 -Creating main dataframe ##########################################################
# df = pd.read_csv("C:\\keshav\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv",usecols=['Exp_date'])

df = pd.read_csv("C:\\keshav\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv",usecols=['Exp_date'])

df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')

df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=entryDaysFromExpiry)      #so we can have time delta
df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
df['entryDt'] = df['entry_date']+' '+entryTime
df['entryDt'] =  pd.to_datetime(df['entryDt'])
df['date'] = df['entryDt'].dt.date
df['time'] = df['entryDt'].dt.date
df.set_index('entryDt',inplace=True)
df = df[['expDateDt', 'date','time']]

# print('-------------------')
# print(df)


#Part2- Banknifty DAtaframe ###################################################################
df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)

# df2= pd.read_csv(f"C:\\Users\\kkark\\oneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)

df2.rename(columns={
                    0   : 'date',
                    1   : 'time',
                    2   : 'open',
                    3   : 'high',
                    4   : 'low',
                    5   : 'close'
},inplace=True)

df2['date'] = pd.to_datetime(df2['date'],format='%Y%m%d').dt.date.astype(str)
df2['datetime'] = df2['date'] + ' ' + df2['time']
df2['datetime'] = pd.to_datetime(df2['datetime'])
df2.set_index('datetime',inplace=True)

#Part3 taking values from banknifty using merge #########################################################
merged_df = pd.merge(df,df2['close'], left_index=True,right_index=True, how='left')


#adding this new column value taken from merged df close column to our df
df['BANKNIFTY_price'] = merged_df['close']


#column --> CE_strike and PE_strike
df['CE_strike'] = (round(df['BANKNIFTY_price']/underlyingStrikeDiff)*underlyingStrikeDiff + strikeDiff).astype(int)
df['PE_strike'] = (round(df['BANKNIFTY_price']/underlyingStrikeDiff)*underlyingStrikeDiff - strikeDiff).astype(int)


#adding relevent entryDate by shifting above one
df.reset_index(inplace=True)
df.insert(0,'relventExpiryDt',df['entryDt'].shift(-1))
df.set_index('entryDt',inplace=True)



#Part4 -Creating Symbol for reading Option file ###############################################################
#Note format underlying+yymmdd+strikeprice+option(CE/PE)
yymmdd =  df['relventExpiryDt'].dt.strftime('%y%m%d')

strikepriceCE = df['CE_strike'].astype('str')
strikepricePE = df['PE_strike'].astype('str')

df['symbolCE'] = underlying+yymmdd+strikepriceCE+'CE'
df['symbolPE'] = underlying+yymmdd+strikepricePE+'PE'


#adding year column for searching symbol
df.insert(0, 'year', df.index.year.astype(str))

df['CEprice'] = np.NaN
df['PEprice'] = np.NaN


#Part5 - Reading realtive option file for each symbol
# reading options


def process_option_data(symbol,option_type):
        option_symbol = df[symbol]
        option_year = df['year']
        dt = df.index
        try:
            # option_df2 = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', f'{option_type}time', f'{option_type}open', f'{option_type}high', f'{option_type}low', f'{option_type}close'])
            
            option_df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', f'{option_type}time', f'{option_type}open', f'{option_type}high', f'{option_type}low', f'{option_type}close'])

            option_df2[f'{option_type}date'] = pd.to_datetime(option_df2[f'{option_type}date'], format='%Y%m%d').dt.date.astype(str)
            option_df2['datetime'] = option_df2[f'{option_type}date'] + ' ' + option_df2[f'{option_type}time']
            option_df2['datetime'] = pd.to_datetime(option_df2['datetime'])
            option_df2.set_index('datetime', inplace=True)

            merge1 = df.merge(option_df2[[f'{option_type}close']], left_index=True, right_index=True, how='left')
            
            print(merge1)


        except FileNotFoundError:
            pass
            
# Call the function for CE symbols
process_option_data('symbolCE','CE')

# Call the function for PE symbols
process_option_data('symbolPE','PE')


df.rename(columns = {
                    'relventExpiryDt': "Entry_relventExpiryDt" ,
                    "expDateDt": "Entry_expDateDt" ,
                    "date": "Entry_date" ,
                    "time": "Entry_time" ,
                    "BANKNIFTY_price": "Entry_BANKNIFTY_price" ,
                    "CE_strike": "Entry_CE_strike" ,
                    "PE_strike": "Entry_PE_strike" ,
                    "symbolCE": "Entry_symbolCE" ,
                    "symbolPE": "Entry_symbolPE" ,
                    "CEprice": "Entry_CEprice" ,
                    "PEprice": "Entry_PEprice" ,
                },inplace=True
                )

df.drop(columns=['Entry_date','Entry_time','Entry_expDateDt'],inplace=True)

#Note by shfting entryDt last value is NaT hence doing ffill
df['Entry_relventExpiryDt'] = df['Entry_relventExpiryDt'].fillna(method='ffill')


####################   Working with Exit Time   #################################################################################
#Part6--> setting exitDt and relevent

df['exitDt'] = df['Entry_relventExpiryDt']+pd.Timedelta(days=exitDaysFromExpiry)
df['exitDt'] = df['exitDt'].dt.date
df['exitDt'] = df['exitDt'].astype(str)
df['exitDt'] = df['exitDt']+' '+exitTime
df['exitDt'] = pd.to_datetime(df['exitDt'])

df['Exit_relventExpiryDt'] = df['Entry_relventExpiryDt']
df.insert(10,'Exit_year',df['exitDt'].dt.year.astype(str))


#part 7 --> calculating banknifty values from df
merged_df2 = pd.merge(df,df2['close'], left_on='exitDt',right_index=True, how='left')

#adding this new column value taken from merged df close column to our df
df['Exit_BANKNIFTY_price'] = merged_df2['close']

df['Exit_CE_strike'] = df['Entry_CE_strike'] 
df['Exit_PE_strike'] = df['Entry_PE_strike']
df['Exit_symbolCE'] = df['Entry_symbolCE']
df['Exit_symbolPE'] = df['Entry_symbolPE']

# #Part8 - Calculating Exit_CEprice and Exit_PEprice reading file for symbol and math with date and capture close price
df['Exit_CEprice'] = np.NaN
df['Exit_PEprice'] = np.NaN


def process_option_data_exit(symbol,option_type):
        option_symbol = df[symbol]
        option_year = df['Exit_year']
        dt = df['exitDt']

        try:
            # option_df2 = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', f'{option_type}time', f'{option_type}open', f'{option_type}high', f'{option_type}low', f'{option_type}close'])

            option_df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', f'{option_type}time', f'{option_type}open', f'{option_type}high', f'{option_type}low', f'{option_type}close'])

            option_df2[f'{option_type}date'] = pd.to_datetime(option_df2[f'{option_type}date'], format='%Y%m%d').dt.date.astype(str)
            option_df2['datetime'] = option_df2[f'{option_type}date'] + ' ' + option_df2[f'{option_type}time']
            option_df2['datetime'] = pd.to_datetime(option_df2['datetime'])
            option_df2.set_index('datetime', inplace=True)

            # print(option_df2)


            # merge2 = df.merge(option_df2[f'{option_type}close'], left_index=True, right_index=True, how='left').fillna(method='ffill')
            # df.loc[dt, f'{option_type}price'] = merge2[f'{option_type}close']

            # print(merge2)


        except FileNotFoundError:
            pass



# Call the function for CE symbols
process_option_data_exit('Exit_symbolCE','CE')

# Call the function for PE symbols
process_option_data_exit('Exit_symbolPE','PE')




print(df.columns)
print(df[['Entry_CEprice', 'Entry_PEprice', 'Exit_CEprice','Exit_PEprice']])
df.to_csv("C:\\keshav\\Rahul\\BankniftyNifty\\excel.csv")