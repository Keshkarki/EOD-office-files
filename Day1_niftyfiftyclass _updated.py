import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)


class ProfitLossCalculator:
    def __init__(self, start_date, end_date,rolling_avg):
            self.rolling_avg = rolling_avg
            self.df = pd.read_csv("C:\\keshav\datasets\\NIFTY 50_Data.csv", parse_dates=['Date'], index_col='Date').sort_index()
            self.df = self.df.loc[start_date:end_date]
            self.calculating_ma()
            self.calculate_signal()
            self.avg_trad_days()
            self.total_PL()

    def calculating_ma(self):
        self.df['Close_MA'] = self.df['Close'].rolling(self.rolling_avg).mean()
    def calculate_signal(self):
        self.df['Signal'] = self.df.apply(lambda row: 'Buy' if (row['Close'] > row['Close_MA']) else ('Sell' if row['Close'] < row['Close_MA'] else '-'), axis=1)
        self.df['Signal'] = self.df['Signal'].shift(1)
        self.df['Signal2'] = self.df['Signal'].shift(1)
        # whenever signal changes track next day open value
        self.df['change'] = self.df.apply(lambda row: row['Open'] if row['Signal']!=row['Signal2'] and row['Signal']!='-' and  row['Signal2'] is not None else '-', axis=1)  

        # convering change column to floats so we can filter it out
        self.df['change'] = self.df.apply(lambda x: float(x['change']) if x['change'] != '-' else 0, axis=1)
    def total_PL(self):
        self.filtered_df = self.df[self.df['change']>0].copy()
        self.filtered_df['shifted_change'] = self.filtered_df['change'].shift(1)
        self.filtered_df['P&L'] = self.filtered_df.apply(lambda row: (row['change'] - row['shifted_change']) if row['Signal'] == 'Sell' else row['shifted_change']-row['change'],axis=1)
        self.filtered_df = self.filtered_df[1:]

        print(f"total P&L : {round(self.filtered_df['P&L'].sum(),2)}")
    def avg_trad_days(self):
        #counting no of days buy or sell inside list
        count_list = []
        count = 0
        last_action = None
        for action in self.df['Signal']:
            if action == 'Buy':
                if last_action != 'Buy':
                    count = 1
                else:
                    count += 1
                last_action = 'Buy'
            elif action == 'Sell':
                if last_action != 'Sell':
                    count = 1
                else:
                    count += 1
                last_action = 'Sell'
            else:
                last_action = None

            count_list.append(count)
            # print(f"{action}: {count}") 

        #added column from list
        self.df['counts'] = count_list
        self.df['Signal'] = self.df['Signal'].fillna(0).replace('-', 0)

        self.temp_df = self.df[['Signal','counts']].copy()
        self.temp_df['shifted_counts'] = self.temp_df['counts'].shift(1)
        self.temp_df['counts2'] = self.temp_df.apply(lambda row: 'count' if row['counts'] < row['shifted_counts'] else '-', axis=1)
        self.temp_df['counts2'] = self.temp_df['counts2'].shift(-1)

        self.temp_df['shifted_signals'] = self.temp_df['Signal'].shift(-1)
        self.temp_df['max_counts'] = self.temp_df.apply(lambda row: row['counts'] if row['Signal']!= row['shifted_signals'] else 0 ,axis=1).astype(int)

        print(f"average buy days : {round(self.temp_df[self.temp_df['max_counts']>0][['Signal','max_counts']].groupby('Signal').mean().values[0][0],2)} ")
        print(f"average sell days : {round(self.temp_df[self.temp_df['max_counts']>0][['Signal','max_counts']].groupby('Signal').mean().values[1][0],2)} ")

        print(f"average total days : {round(self.temp_df[self.temp_df['max_counts']>0][['Signal','max_counts']]['max_counts'].mean(),2)} ")


obj1 = ProfitLossCalculator('2018-04-02', '2023-04-21',20)      #start date - end date - rolling avg

obj2 = ProfitLossCalculator('2020-04-02', '2023-04-21',25)      #start date - end date - rolling avg


