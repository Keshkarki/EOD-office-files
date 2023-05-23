import numpy as np
import pandas as pd

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

    def process_option_data(self, symbol, option_type):
        for i, row in self.df.iterrows():
            option_symbol = row[symbol]
            option_year = row['year']
            dt = row.name

            try:
                option_df2 = pd.read_csv(f"C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{option_year}\\{self.underlying} Options\\{option_symbol}.csv", header=None, usecols=[0, 1, 2, 3, 4, 5], names=[f'{option_type}date', 'strike', 'expiry', 'option_type', 'open', 'close'])

                option_df2[f'{option_type}date'] = pd.to_datetime(option_df2[f'{option_type}date'], format='%Y%m%d').dt.date.astype(str)
                option_df2.set_index(f'{option_type}date', inplace=True)

                option_df2[f'{option_type}time'] = option_df2.index + ' ' + option_df2['time']
                option_df2[f'{option_type}time'] = pd.to_datetime(option_df2[f'{option_type}time'])
                option_df2.drop(columns=['time'], inplace=True)

                option_df2[f'{option_type}datetime'] = pd.to_datetime(option_df2[f'{option_type}time'], format='%Y-%m-%d %H:%M:%S')

                self.merged_df = pd.merge(self.merged_df, option_df2['close'], left_index=True, right_index=True, how='left')

            except Exception as e:
                print(f"Error reading file for {option_symbol}: {e}")
                continue

        self.merged_df.rename(columns={'close': f'{option_type} close'}, inplace=True)
        self.merged_df.dropna(subset=[f'{option_type} close'], inplace=True)
        self.merged_df.reset_index(inplace=True)

        return self.merged_df

# Usage example
processor = OptionDataProcessor()
processor.load_weekly_expiry_dates("C:\\Users\\kkark\\OneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv")
processor.load_banknifty_data(f"C:\\Users\\kkark\\oneDrive\\Desktop\\OFFICE_FILES\\EOD-office-files\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{underlying}.csv")
processor.merge_dataframes()
merged_data = processor.process_option_data('symbol', 'option_type')
