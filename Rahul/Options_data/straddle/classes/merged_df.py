# %%

import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

class MergedDataFrame:
    """ merged_df = obj.get_merged_df()\n-alywas run this command after object creation so it can store value of merged df and we will use it further also print(obj.guide()) for more detailed docstrings"""
    
    
    def __init__(self, underlying):
        self.underlying = underlying

    def _read_bank_nifty_df(self):
        bank_nifty_df = pd.read_csv(f'C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{self.underlying}.csv', header=None)
        bank_nifty_df.rename(columns={
            0: 'date',
            1: 'time',
            2: 'open',
            3: 'high',
            4: 'low',
            5: 'close'
        }, inplace=True)
        bank_nifty_df['date'] = bank_nifty_df['date'].astype('str')
        datetime = pd.to_datetime(bank_nifty_df['date'] + ' ' + bank_nifty_df['time'], format='%Y%m%d %H:%M')
        bank_nifty_df.insert(1, 'datetime', datetime)
        bank_nifty_df['date'] = pd.to_datetime(bank_nifty_df['date'])
        bank_nifty_df.set_index('datetime', inplace=True)
        bank_nifty_df = bank_nifty_df.between_time('09:15:00', '15:29:00')
        return bank_nifty_df

    def _calculate_exp_dates(self, bank_nifty_df):
        x = sorted(list(set(bank_nifty_df.index.date)))
        x = pd.to_datetime(x)

        unique_date_list = [date.strftime("%Y-%m-%d") for date in x]
        weekly_exp_df = pd.read_csv("C:\keshav\Rahul\Options_data\Weekly_exp_dates.csv", usecols=['Exp_date'])
        weekly_exp_df['Exp_date'] = pd.to_datetime(weekly_exp_df['Exp_date'], format='%d-%b-%y')
        weekly_exp_df['day'] = weekly_exp_df['Exp_date'].dt.day
        weekly_exp_df['monthly_exp'] = False

        for i in range(len(weekly_exp_df)):
            try:
                if weekly_exp_df.loc[i, 'day'] > weekly_exp_df.loc[i + 1, 'day']:
                    weekly_exp_df.loc[i, 'monthly_exp'] = True

                monthly_exp_df = pd.DataFrame()
                monthly_exp_df = weekly_exp_df.loc[(weekly_exp_df['monthly_exp'] == True), ['Exp_date', 'day']]

                df_weekly_list = weekly_exp_df[['Exp_date']]
                df_monthly_list = monthly_exp_df[['Exp_date']]

                df_datelist = pd.DataFrame(bank_nifty_df['date'].unique(), columns=['date'])
                df_datelist[['currWeek_exp_dt', 'nextWeek_exp_dt', 'farWeek_exp_dt', 'currMonth_exp_dt',
                             'nextMonth_exp_dt', 'farMonth_exp_dt']] = np.NaN

            except:
                pass

        for i in range(len(df_datelist)):
            try:
                df2 = df_weekly_list.loc[df_weekly_list['Exp_date'] >= df_datelist['date'][i]]
                df_datelist.loc[i, 'currWeek_exp_dt'] = df2['Exp_date'].values[0]
                df_datelist.loc[i, 'nextWeek_exp_dt'] = df2['Exp_date'].values[1]
                df_datelist.loc[i, 'farWeek_exp_dt'] = df2['Exp_date'].values[2]
                df3 = df_monthly_list.loc[df_monthly_list['Exp_date'] >= df_datelist['date'][i]]

                df_datelist.loc[i, 'currMonth_exp_dt'] = df3['Exp_date'].values[0]
                df_datelist.loc[i, 'nextMonth_exp_dt'] = df3['Exp_date'].values[1]
                df_datelist.loc[i, 'farMonth_exp_dt'] = df3['Exp_date'].values[2]

            except:
                pass

        merged_df = pd.merge(bank_nifty_df, df_datelist, how='left', on='date')
        merged_df['currWeek_exp_dt'] = pd.to_datetime(merged_df['currWeek_exp_dt']).dt.date
        merged_df['nextWeek_exp_dt'] = pd.to_datetime(merged_df['nextWeek_exp_dt']).dt.date
        merged_df['farWeek_exp_dt'] = pd.to_datetime(merged_df['farWeek_exp_dt']).dt.date
        merged_df['currMonth_exp_dt'] = pd.to_datetime(merged_df['currMonth_exp_dt']).dt.date
        merged_df['nextMonth_exp_dt'] = pd.to_datetime(merged_df['nextMonth_exp_dt']).dt.date
        merged_df['farMonth_exp_dt'] = pd.to_datetime(merged_df['farMonth_exp_dt']).dt.date

        merged_df['date'] = merged_df['date'].astype(str)
        merged_df['time'] = merged_df['time'].astype(str)
        datetime = pd.to_datetime(merged_df['date'] + ' ' + merged_df['time'], format='mixed', dayfirst=True)
        bank_nifty_df.index = pd.to_datetime(bank_nifty_df.index)
        merged_df.insert(0, 'datetime', datetime)
        merged_df.set_index('datetime', inplace=True)
        merged_df.drop(columns=['date', 'time'], inplace=True)

        merged_df.insert(4, 'ATMStrPr', round(merged_df['close'], -2))
        return merged_df

    def get_merged_df(self):
        bank_nifty_df = self._read_bank_nifty_df()
        merged_df = self._calculate_exp_dates(bank_nifty_df)
        return merged_df
    

    def guide(self):
        print('merged_df = merged_df_obj.get_merged_df()\n-alywas run this command after object creation so it can store value of merged df and we will use it further \n also same underying should be pass in antoher classes using this class')


merged_df_obj = MergedDataFrame(underlying='BANKNIFTY')