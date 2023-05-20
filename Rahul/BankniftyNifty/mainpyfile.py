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
# df = pd.read_csv("Weekly_exp_dates.csv",usecols=['Exp_date'])

df = pd.read_csv("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv",usecols=['Exp_date'])
df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')

df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=entryDaysFromExpiry)      #so we can have time delta
df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
df['entryDt'] = df['entry_date']+' '+entryTime
df['entryDt'] =  pd.to_datetime(df['entryDt'])
df['date'] = df['entryDt'].dt.date
df['time'] = df['entryDt'].dt.date
df.set_index('entryDt',inplace=True)
df = df[['expDateDt', 'date','time']]

# print(df)



#Part2- Banknifty DAtaframe ###################################################################
# df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)

df2= pd.read_csv(f"C:\\Users\\kkark\\oneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)

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
# print("BankNifty_dataframe",df2)

#Part3 taking vaues from banknifty using merge #########################################################
merged_df = pd.merge(df,df2['close'], left_index=True,right_index=True, how='left')
# print(merged_df)

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
df['year']=df['expDateDt'].dt.year.astype(str)
df['CEprice'] = np.NaN
df['PEprice'] = np.NaN
# print(df.iloc[:,6:])


#Part5 - Reading realtive option file for each symbol
# reading options
# rel_PE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{df['date'].iloc[0]}\\{underlying} Options\\{df['symbolCE'].iloc[0]}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

# rel_PE_df = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\2022\\{underlying} Options\\BANKNIFTY22120143500CE.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])


# Iterate over each row of the DataFrame and update CEprice
for i, row in df.iterrows():
    ce_symbol = row['symbolCE']
    ce_year = row['year']
    dt = row.name

    try:
        # Read the corresponding CSV file
        rel_PE_df = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{ce_year}\\{underlying} Options\\{ce_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

        rel_PE_df['CEdate'] = pd.to_datetime(rel_PE_df['CEdate'],format='%Y%m%d').dt.date.astype(str)
        rel_PE_df['datetime'] = rel_PE_df['CEdate'] + ' ' + rel_PE_df['CEtime']
        rel_PE_df['datetime'] = pd.to_datetime(rel_PE_df['datetime'])
        rel_PE_df.set_index('datetime',inplace=True)

        if dt in rel_PE_df.index:
            # Update the CEprice column in the original DataFrame
            PEpriceValue = rel_PE_df.loc[dt, 'CEclose']
            df.loc[dt, 'CEprice'] = PEpriceValue
        else:
            df.loc[dt, 'CEprice'] = np.NaN


    except FileNotFoundError:
        # print(f"File not found for {ce_symbol} in {ce_year}")
        pass


# ##For PE
for i, row in df.iterrows():
    pe_symbol = row['symbolPE']
    ce_year = row['year']
    dt = row.name

    try:
        # Read the corresponding CSV file
        rel_PE_df = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{ce_year}\\{underlying} Options\\{pe_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])

        rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date.astype(str)
        rel_PE_df['datetime'] = rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime']
        rel_PE_df['datetime'] = pd.to_datetime(rel_PE_df['datetime'])
        rel_PE_df.set_index('datetime',inplace=True)

        if dt in rel_PE_df.index:
            # Update the PEprice column in the original DataFrame
            PEpriceValue = rel_PE_df.loc[dt, 'PEclose']
            df.loc[dt, 'PEprice'] = PEpriceValue
        else:
            df.loc[dt, 'PEprice'] = np.NaN


    except FileNotFoundError:
        pass

# df.to_csv('Entry_Price3.csv')

#Renaming and keeping only required columns

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
                    "year": "Entry_year" ,
                    "CEprice": "Entry_CEprice" ,
                    "PEprice": "Entry_PEprice" ,
                },inplace=True
                )

df.drop(columns=['Entry_date','Entry_time','Entry_expDateDt'],inplace=True)

#Note by shifring entryDt last value is NaT hence doing ffill
df['Entry_relventExpiryDt'] = df['Entry_relventExpiryDt'].fillna(method='ffill')









####################   Working with Exit Time   #################################################################################
#Part6--> setting exitDt and relevent

df['exitDt'] = df['Entry_relventExpiryDt']+pd.Timedelta(days=exitDaysFromExpiry)
df['exitDt'] = df['exitDt'].dt.date
df['exitDt'] = df['exitDt'].astype(str)
df['exitDt'] = df['exitDt']+' '+exitTime
df['exitDt'] = pd.to_datetime(df['exitDt'])

df['Exit_relventExpiryDt'] = df['Entry_relventExpiryDt']


#part 7 --> calculating banknifty values from df
merged_df2 = pd.merge(df,df2['close'], left_on='exitDt',right_index=True, how='left')

#adding this new column value taken from merged df close column to our df
df['Exit_BANKNIFTY_price'] = merged_df2['close']
df['Exit_CE_strike'] = df['Entry_CE_strike'] 
df['Exit_PE_strike'] = df['Entry_PE_strike']
df['Exit_symbolCE'] = df['Entry_symbolCE']
df['Exit_symbolPE'] = df['Entry_symbolPE']
df['Exit_year'] = df['Entry_year']


#Part8 - Calculating Exit_CEprice and Exit_PEprice reading file for symbol and math with date and capture close price
df['Exit_CEprice'] = np.NaN
df['Exit_PEprice'] = np.NaN



# Iterate over each row of the DataFrame and update Exit_CEprice
for i, row in df.iterrows():
    ce_symbol = row['Exit_symbolCE']
    ce_year = row['Exit_year']
    dt = df['exitDt'][i]

    try:
        rel_PE_df = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{ce_year}\\{underlying} Options\\{ce_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

        rel_PE_df['CEdate'] = pd.to_datetime(rel_PE_df['CEdate'],format='%Y%m%d').dt.date.astype(str)
        rel_PE_df['datetime'] = rel_PE_df['CEdate'] + ' ' + rel_PE_df['CEtime']
        rel_PE_df['datetime'] = pd.to_datetime(rel_PE_df['datetime'])
        rel_PE_df.set_index('datetime',inplace=True)


        if dt in rel_PE_df.index:
            PEpriceValue = rel_PE_df.loc[dt, 'CEclose']
            df.loc[df['exitDt']==dt, 'Exit_CEprice'] = PEpriceValue
        else:
            df.loc[df['exitDt']==dt, 'Exit_CEprice'] = PEpriceValue= np.NaN


    except FileNotFoundError:
        # print(f"File not found for {ce_symbol} in {ce_year}")
        pass


# Iterate over each row of the DataFrame and update Exit_PEprice
for i, row in df.iterrows():
    pe_symbol = row['Exit_symbolPE']
    pe_year = row['Exit_year']
    dt = df['exitDt'][i]

    try:
        rel_PE_df = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{pe_year}\\{underlying} Options\\{pe_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])

        rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date.astype(str)
        rel_PE_df['datetime'] = rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime']
        rel_PE_df['datetime'] = pd.to_datetime(rel_PE_df['datetime'])
        rel_PE_df.set_index('datetime',inplace=True)


        if dt in rel_PE_df.index:
            PEpriceValue = rel_PE_df.loc[dt, 'PEclose']
            df.loc[df['exitDt']==dt, 'Exit_PEprice'] = PEpriceValue
        else:
            df.loc[df['exitDt']==dt, 'Exit_PEprice'] = PEpriceValue= np.NaN


    except FileNotFoundError:
        # print(f"File not found for {pe_symbol} in {pe_year}")
        pass

df.to_csv("final_df_sat.csv")