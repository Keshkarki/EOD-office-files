import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta


underlying = 'BANKNIFTY'

class OptionDataProcessor:
    def __init__(self):
        pd.set_option('display.max_colwidth', None)
        
        self.entryDaysFromExpiry = 0
        self.exitDaysFromExpiry = 0
        self.entryTime = '15:15'
        self.exitTime = '15:15'
        self.strikeDiff = 100                 
        self.underlyingStrikeDiff = 50              
        self.underlying = 'BANKNIFTY'


        self.underlyingStrikeDiff = 100 if self.underlying == 'BANKNIFTY' else 50

        self.OTM_points = 100

        self.df = None
        self.df2 = None
        self.merged_df = None
        self.renaming() 



    def load_weekly_expiry_dates(self, file_path):
        self.df = pd.read_csv(file_path, usecols=['Exp_date'])
        self.df['expDateDt'] = pd.to_datetime(self.df['Exp_date'], format='%d-%b-%y')
        self.df['entry_date'] = self.df['expDateDt'] - pd.Timedelta(days=self.entryDaysFromExpiry)
        self.df['entry_date'] = self.df['entry_date'].astype('str')
        self.df['entryDt'] = self.df['entry_date'] + ' ' + self.entryTime
        self.df['entryDt'] = pd.to_datetime(self.df['entryDt'])
        self.df['date'] = self.df['entryDt'].dt.date
        self.df['time'] = self.df['entryDt'].dt.date
        self.df.set_index('entryDt', inplace=True)
        self.df = self.df[['expDateDt', 'date', 'time']]



    def load_banknifty_data(self, file_path):
        self.df2 = pd.read_csv(file_path, header=None)
        self.df2.rename(columns={
            0: 'date',
            1: 'time',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close'
        }, inplace=True)
        self.df2['date'] = pd.to_datetime(self.df2['date'], format='%Y%m%d').dt.date.astype(str)
        self.df2['datetime'] = self.df2['date'] + ' ' + self.df2['time']
        self.df2['datetime'] = pd.to_datetime(self.df2['datetime'])
        self.df2.set_index('datetime', inplace=True)



    def merge_dataframes(self):
        self.merged_df = pd.merge(self.df, self.df2['close'], left_index=True, right_index=True, how='left')


    def modify_df(self):
        self.df['BANKNIFTY_price'] = self.merged_df['close']

        #column --> CE_strike and PE_strike
        self.df['CE_strike'] = (round(self.df['BANKNIFTY_price']/self.underlyingStrikeDiff)*self.underlyingStrikeDiff + self.strikeDiff).astype(int)
        self.df['PE_strike'] = (round(self.df['BANKNIFTY_price']/self.underlyingStrikeDiff)*self.underlyingStrikeDiff - self.strikeDiff).astype(int)


    #adding relevent entryDate by shifting above one
        self.df.reset_index(inplace=True)
        self.df.insert(0,'relventExpiryDt',self.df['entryDt'].shift(-1))
        self.df.set_index('entryDt',inplace=True)


    def  symbol(self):
        #Note format underlying+yymmdd+strikeprice+option(CE/PE)
        yymmdd =  self.df['relventExpiryDt'].dt.strftime('%y%m%d')

        strikepriceCE = self.df['CE_strike'].astype('str')
        strikepricePE = self.df['PE_strike'].astype('str')

        self.df['symbolCE'] = underlying+yymmdd+strikepriceCE+'CE'
        self.df['symbolPE'] = underlying+yymmdd+strikepricePE+'PE'


        #adding year column for searching symbol
        self.df['year']=self.df.index.year.astype(str)
        self.df['CEprice'] = np.NaN
        self.df['PEprice'] = np.NaN



    def process_option_data_entry(self, symbol, option_type):
        for i, row in self.df.iterrows():
            option_symbol = row[symbol]
            option_year = row['year']
            dt = row.name

            try:
                option_df2 = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{self.underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', f'{option_type}time', f'{option_type}open', f'{option_type}high', f'{option_type}low', f'{option_type}close'])

                option_df2[f'{option_type}date'] = pd.to_datetime(option_df2[f'{option_type}date'], format='%Y%m%d').dt.date.astype(str)
                option_df2['datetime'] = option_df2[f'{option_type}date'] + ' ' + option_df2[f'{option_type}time']
                option_df2['datetime'] = pd.to_datetime(option_df2['datetime'])
                option_df2.set_index('datetime', inplace=True)

                if dt in option_df2.index:
                    price_value = option_df2.loc[dt, f'{option_type}close']
                    self.df.loc[dt, f'{option_type}price'] = price_value
                else:
                    self.df.loc[dt, f'{option_type}price'] = np.NaN

            except FileNotFoundError:
                pass


    def renaming(self):
        self.df.rename(columns={
        'relventExpiryDt': "Entry_relventExpiryDt",
        "expDateDt": "Entry_expDateDt",
        "date": "Entry_date",
        "time": "Entry_time",
        "BANKNIFTY_price": "Entry_BANKNIFTY_price",
        "CE_strike": "Entry_CE_strike",
        "PE_strike": "Entry_PE_strike",
        "symbolCE": "Entry_symbolCE",
        "symbolPE": "Entry_symbolPE",
        "CEprice": "Entry_CEprice",
        "PEprice": "Entry_PEprice",
    }, inplace=True)

        self.df.drop(columns=['Entry_date', 'Entry_time', 'Entry_expDateDt'], inplace=True)

        # Fill NaN values in 'Entry_relventExpiryDt' column using forward-fill (ffill) method
        self.df['Entry_relventExpiryDt'] = self.df['Entry_relventExpiryDt'].fillna(method='ffill')
        print('hiiii')




# Usage example
processor = OptionDataProcessor()

processor.load_weekly_expiry_dates("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv")

processor.load_banknifty_data(f"C:\\Users\\kkark\\oneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv")

processor.merge_dataframes()
processor.modify_df()
processor.symbol()

# Call the method for CE symbols
processor.process_option_data_entry('symbolCE', 'CE')

# Call the method for PE symbols
processor.process_option_data_entry('symbolPE', 'PE')
processor.renaming()


#office file path
# df = pd.read_csv("C:\\keshav\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv",usecols=['Exp_date'])

# df2 = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv",header=None)