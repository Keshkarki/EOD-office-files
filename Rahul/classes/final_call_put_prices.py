# %%
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime


# %%
from _01_merged_df import MergedDataFrame 
obj = MergedDataFrame(underlying='BANKNIFTY')
merged_df = obj.get_merged_df()
merged_df

#   %%

class Prices:

    def __init__ (self, merged_df, underlying, date, time, exp_period, OTM_point ):

        # initializing 
        
        self.merged_df = merged_df
        self.underlying = underlying
        self.date = date
        self.time = time
        self.exp_period = exp_period
        self.OTM_points = OTM_point

        self.dateStr = date.split('-')[0]
        

        self.dateTimeStr = date+' '+time
        self.datetime_obj = datetime.strptime(self.dateTimeStr, '%Y-%m-%d %H:%M')
        self.timeDt = self.datetime_obj.time()
        self.dateDt = self.datetime_obj.date()

        self.symbol()
        self.rel_ce_df_method()
        self.rel_pe_df_method()

    def symbol(self):
            ###  expiryDate formatting for symbol
            expDate = self.merged_df.loc[self.datetime_obj,self.exp_period]
            expDate = expDate.strftime('%y%m%d')

            # strike prices
            CE_strikePrice = str(round(merged_df.loc[(merged_df.index.time == self.timeDt) & (merged_df.index.date == self.dateDt), 'ATMStrPr'].values[0] + self.OTM_points))
            # print(CE_strikePrice)

            PE_strikePrice = str(round(merged_df.loc[(merged_df.index.time == self.timeDt) & (merged_df.index.date == self.dateDt), 'ATMStrPr'].values[0] - self.OTM_points))
            # print(PE_strikePrice)

            CE_symbol = self.underlying+expDate+CE_strikePrice+'CE'
            PE_symbol = self.underlying+expDate+PE_strikePrice+'PE'
            self.CE_symbol = CE_symbol
            self.PE_symbol = PE_symbol

    def rel_ce_df_method(self):
        rel_CE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.dateStr}\\{self.underlying} Options\\{self.CE_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['date', 'time', 'open', 'high', 'low', 'close'])

        rel_CE_df['date'] = pd.to_datetime(rel_CE_df['date'],format='%Y%m%d').dt.date
        rel_CE_df['date'] = pd.to_datetime(rel_CE_df['date'])
        rel_CE_df['date'] = rel_CE_df['date'].astype('str')
        datetime = pd.to_datetime(rel_CE_df['date'] + ' ' + rel_CE_df['time'], format='%Y-%m-%d %H:%M')
        rel_CE_df.set_index(datetime,inplace=True)
        call_price = rel_CE_df.loc[self.datetime_obj,'close']
        self.call_price = call_price


    def rel_pe_df_method(self):
        rel_PE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.dateStr}\\{self.underlying} Options\\{self.PE_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['date', 'time', 'open', 'high', 'low', 'close'])

        rel_PE_df['date'] = pd.to_datetime(rel_PE_df['date'],format='%Y%m%d').dt.date
        rel_PE_df['date'] = pd.to_datetime(rel_PE_df['date'])
        rel_PE_df['date'] = rel_PE_df['date'].astype('str')
        datetime = pd.to_datetime(rel_PE_df['date'] + ' ' + rel_PE_df['time'], format='%Y-%m-%d %H:%M')
        rel_PE_df.set_index(datetime,inplace=True)
        put_price = rel_PE_df.loc[self.datetime_obj,'close']
        self.put_price = put_price


obj = Prices(merged_df = merged_df, underlying='BANKNIFTY', date='2022-02-01', time= '09:19' , exp_period='currWeek_exp_dt', OTM_point=100)

print(f"Call Price : {obj.call_price}")
print(f"put Price : {obj.put_price}")





print(obj.CE_symbol)
print(obj.PE_symbol)

# %%






