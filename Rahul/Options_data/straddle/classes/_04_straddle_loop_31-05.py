# unique_dates variable added
# taking value from merged_df


# %%
import numpy as np
import pandas as pd
from _01_merged_df import MergedDataFrame

obj = MergedDataFrame(underlying='BANKNIFTY')
merged_df = obj.get_merged_df() 
unique_dates = obj.get_unique_dates()

# %%
    
class Straddle:
    def __init__(self,merged_df, date, exp_period, underlying,
                 start_time, entry_time, exit_time, end_time,
                 entry_side, OTM_points,
                 straddle_SL_pct, straddle_tgt_pct):
        
        """ print(obj.guide() for guideline/docstrings)"""

        self.date = date
        self.underlying = underlying
        self.merged_df = merged_df
        self.exp_period = exp_period

        self.datestr = self.date.split('-')[0]
        self.start_time = start_time
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.end_time = end_time
        self.entry_side = entry_side

        self.underlying_strike_diff = 100 if underlying == 'BANKNIFTY' else 50
        self.OTM_points = OTM_points
        self.straddle_SL_pct = straddle_SL_pct        #0.2 -> 20%
        self.straddle_tgt_pct =straddle_tgt_pct  #0.8 --> 80%


        #conversion
        self.date_dt = pd.to_datetime(date).date()
        self.entry_time_dt = pd.to_datetime(self.entry_time).time()
        self.exit_time_dt = pd.to_datetime(self.exit_time).time()
        self.end_time_dt = pd.to_datetime(self.end_time).time()

        #for filtering and adding hit status between  index which is first hit and exit_timestamp
        self.datetime_str = f'{self.date} {self.exit_time}'
        self.exit_timestamp = pd.to_datetime(self.datetime_str)


        #for function working to call
        self.CE_strike_prices(self.entry_time_dt,self.date_dt)
        self.PE_strike_prices(self.entry_time_dt,self.date_dt)
        self.calculate_strikes()

        self.exp_date = self.exp_date_loc(self.entry_time_dt, self.date_dt, self.exp_period)
                 # Generate symbols
        self.ce_symbol = f"{self.underlying}{self.exp_date}{self.CE_stp}CE"
        self.pe_symbol = f"{self.underlying}{self.exp_date}{self.PE_stp}PE"


        #calling reading_CE_df
        self.rel_CE_df =  self.reading_CE_df()

        #calling reading_PE_df
        self.rel_PE_df = self.reading_PE_df()

        #making straddle_df
        self.straddle_df = self.making_straddle_df()


    def CE_strike_prices(self,entry_time_dt,date_dt):
        return str(round(self.merged_df.loc[(self.merged_df.index.time == self.entry_time_dt) & (self.merged_df.index.date == self.date_dt), 'ATMStrPr'].values[0] + self.OTM_points))
    

    def PE_strike_prices(self,entry_time_dt,date_dt):
        return str(round(self.merged_df.loc[(self.merged_df.index.time == self.entry_time_dt) & (self.merged_df.index.date == self.date_dt), 'ATMStrPr'].values[0] - self.OTM_points))
    
    def calculate_strikes(self):
        CE_stp = self.CE_strike_prices(self.entry_time_dt, self.date_dt)
        PE_stp = self.PE_strike_prices(self.entry_time_dt, self.date_dt)

        self.merged_df['CE_strike_price'] = CE_stp
        self.merged_df['PE_strike_price'] = PE_stp

        self.CE_stp = CE_stp
        self.PE_stp = PE_stp


    def exp_date_loc(self, entry_time_dt, date_dt, exp_period):
        result = self.merged_df.loc[(self.merged_df.index.time == entry_time_dt) & (self.merged_df.index.date == date_dt)][exp_period]
        result = result.values[0]
        date = pd.to_datetime(result)
        formatted_date = date.strftime('%y%m%d')
        return formatted_date
    


    def reading_CE_df(self):
        try:
            path = f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.datestr}\\{self.underlying} Options\\{self.ce_symbol}.csv"
            
            rel_CE_df = pd.read_csv(path,header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

            rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'],format='%Y%m%d').dt.date
            rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'])
            rel_CE_df['CEdate'] = rel_CE_df['CEdate'].astype('str')
            CEdatetime = pd.to_datetime(rel_CE_df['CEdate'] + ' ' + rel_CE_df['CEtime'], format='%Y-%m-%d %H:%M')
            rel_CE_df.set_index(CEdatetime,inplace=True)
            rel_CE_df=rel_CE_df.loc[self.date]
            return rel_CE_df
        
        except:
            print('File path is not valid')
    

    def reading_PE_df(self):
        try:
            path = f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.datestr}\\{self.underlying} Options\\{self.pe_symbol}.csv"
            rel_PE_df = pd.read_csv(path,header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])
            rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date
            rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'])
            rel_PE_df['PEdate'] = rel_PE_df['PEdate'].astype('str')

            PEdatetime = pd.to_datetime(rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime'], format='%Y-%m-%d %H:%M')
            rel_PE_df.set_index(PEdatetime,inplace=True)

            rel_PE_df=rel_PE_df.loc[self.date]
            return rel_PE_df
        
        except:
            print('file path is not valid')



    def making_straddle_df(self):

        straddle_df = pd.merge(self.rel_CE_df,self.rel_PE_df, left_index=True, right_index=True)
        straddle_df['straddle_open'] = straddle_df['CEopen']  + straddle_df['PEopen']
        straddle_df['straddle_high'] = np.maximum(straddle_df['CEhigh'] + straddle_df['PElow'],straddle_df['CElow'] + straddle_df['PEhigh'])
        straddle_df['straddle_low'] = np.minimum(straddle_df['CEhigh'] + straddle_df['PElow'],straddle_df['CElow'] + straddle_df['PEhigh'])
        straddle_df['straddle_close'] = straddle_df['CEclose']  + straddle_df['PEclose']

        straddle_df = straddle_df[['straddle_open','straddle_high','straddle_low','straddle_close']]

        #Creating  stradle_entryPrice column
        straddle_entryPriceValue = straddle_df.loc[straddle_df.index.time == self.entry_time_dt ]['straddle_close'].values[0]


        straddle_df['straddle_entryPrice'] = np.NaN
        straddle_df.loc[straddle_df.index.time > self.entry_time_dt, 'straddle_entryPrice'] = straddle_entryPriceValue

        #Creating straddle_stoploss
        straddle_df['straddle_stoploss'] =np.NaN

        if self.entry_side =='sell':
            straddle_df.loc[straddle_df.index.time > self.entry_time_dt, 'straddle_stoploss'] = straddle_entryPriceValue*(1+self.straddle_SL_pct)

        else:
            straddle_df.loc[straddle_df.index.time > self.entry_time_dt, 'straddle_stoploss'] = straddle_entryPriceValue*(1- self.straddle_SL_pct)      


        #Creating target
        straddle_df['straddle_tgt'] = np.NaN

        if self.entry_side == 'sell':
            straddle_df.loc[straddle_df.index.time > self.entry_time_dt, 'straddle_tgt'] = straddle_entryPriceValue*(1 - self.straddle_tgt_pct)

        else:
            straddle_df.loc[straddle_df.index.time > self.entry_time_dt, 'straddle_tgt'] = straddle_entryPriceValue*(1 + self.straddle_tgt_pct)

        # #Creating stradle_SL_hit
        straddle_df['stradle_SLhit'] = np.where(straddle_df['straddle_high'] >= straddle_df['straddle_stoploss'], 1, 0)

        #Creating stradle_Tgthit
        straddle_df['stradle_Tgthit'] = np.where(straddle_df['straddle_low'] <= straddle_df['straddle_tgt'], 1, 0)

        #--->calculating straddle_hit_status
        #Creating hitType column whether SL/TGT/Squreoff
        condition1 = straddle_df['stradle_SLhit'] == 1
        condition2 = straddle_df['stradle_Tgthit']==1
        condition3 = straddle_df.index.time == self.exit_time_dt

        straddle_df['straddle_hit_status'] = ''
        straddle_df.loc[condition1, 'straddle_hit_status'] = 'SL_hit'
        straddle_df.loc[condition2, 'straddle_hit_status'] = 'TGThit'
        straddle_df.loc[condition3, 'straddle_hit_status'] = 'squareoff'


        first_non_null = straddle_df[straddle_df['straddle_hit_status'] != '']['straddle_hit_status'].iloc[0]
        straddle_df['straddle_hit_status'] = np.where(straddle_df['straddle_hit_status'] != '', first_non_null,'')

        mask = straddle_df['straddle_hit_status'] == first_non_null
        index_position = straddle_df.index[mask].tolist()[0]

        straddle_df.loc[((straddle_df.index > index_position) & (straddle_df.index < self.exit_timestamp)), 'straddle_hit_status'] = first_non_null


        # #--->Calcuating straddle_exitPrice column
        straddle_df['straddle_exitPrice'] = np.NaN
        straddle_df.loc[straddle_df['straddle_hit_status'] == 'SL_hit','straddle_exitPrice'] = straddle_df['straddle_stoploss']
        straddle_df.loc[straddle_df['straddle_hit_status'] == 'TGThit','straddle_exitPrice'] = straddle_df['straddle_tgt']
        straddle_df.loc[straddle_df['straddle_hit_status'] == 'squareoff','straddle_exitPrice'] = straddle_df['straddle_close']

        #--->Calcuating straddle_MTM column
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_MTM'] = np.where(condition, straddle_df['straddle_entryPrice'] - straddle_df['straddle_close'], np.nan)

        #--->Calcuating straddle_highMTM (entryprice-low)
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_highMTM'] = np.where(condition, straddle_df['straddle_entryPrice'] - straddle_df['straddle_low'], np.nan)

        #--->Calcuating straddle_maxMTM
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_maxMTM'] = np.where(condition,np.where(straddle_df['straddle_highMTM'].cummax() > 0 ,straddle_df['straddle_highMTM'].cummax() ,np.nan),np.nan)

        #--->Calcuating CE_lowMTM  (entryprice-high)
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_lowMTM'] = np.where(condition, straddle_df['straddle_entryPrice'] - straddle_df['straddle_high'], np.nan)

        #--->Calcuating straddle_minMTM
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_minMTM'] = np.where(condition,straddle_df['straddle_lowMTM'].cummin(), np.nan)

        #--->Calcuating straddle_PnL column
        condition = (straddle_df.index.time >= self.entry_time_dt) & (straddle_df.index.time <= self.end_time_dt)
        straddle_df['straddle_PnL'] = np.where(condition, straddle_df['straddle_entryPrice'] - straddle_df['straddle_exitPrice'], np.nan)

        return straddle_df
    


    # def guide(self):
    #     print(f"1. merged_df which is dataframe with all expiry dates for underying should be run first ")
    #     print(f"2. Dates should have format like 'yyyy-mm-dd' ")
    #     print(f"3. time should have format like '09:15' n")
    #     print(f"4. choose underlying as from ['BANKNIFTY','NIFTY'] ")
    #     print(f"5. choose exp_period from ['currWeek_exp_dt', 'nextWeek_exp_dt', 'farWeek_exp_dt','currMonth_exp_dt', 'nextMonth_exp_dt', 'farMonth_exp_dt' ] ")
    #     print(f"6. straddle_sl_pct and straddle_tgt_pct should be in decimal like 0.2 represent 20% ")
    #     print(f"7. In entry_side use one of ['buy,sell]")
    #     print(f"8. obj.get_unique_dates() call this function first to get unique dates from merged_df and use in this function")

    # def to_csv(self):
    #     self.straddle_df.to_excel('Straddle_df.xlsx')


    def get_result_row(self):
        #getting last row close values 
        date = self.straddle_df.index.date[0]

        straddle_close = self.straddle_df['straddle_close'][self.straddle_df['straddle_close'].last_valid_index()]

        straddle_entryPrice = self.straddle_df['straddle_entryPrice'][self.straddle_df['straddle_entryPrice'].last_valid_index()]

        non_blank_list = self.straddle_df['straddle_hit_status'][self.straddle_df['straddle_hit_status'].values !='']

        straddle_hit_status = non_blank_list[non_blank_list.last_valid_index()]

        try:
            straddle_maxMTM = self.straddle_df['straddle_maxMTM'][self.straddle_df['straddle_maxMTM'].last_valid_index()]

        except:
            straddle_maxMTM = 0

        try:
            straddle_minMTM = self.straddle_df['straddle_minMTM'][self.straddle_df['straddle_minMTM'].last_valid_index()]

        except:
           straddle_minMTM = 0

        straddle_PnL = self.straddle_df['straddle_PnL'][self.straddle_df['straddle_PnL'].last_valid_index()]

        result_df = pd.DataFrame(columns=['date','straddle_close','straddle_entryPrice', 'straddle_hit_status', 'straddle_minMTM','straddle_maxMTM','straddle_PnL'])

        result_df.loc[0,"date"] = date
        result_df.loc[0,"straddle_close"] = straddle_close
        result_df.loc[0,"straddle_entryPrice"] = straddle_entryPrice
        result_df.loc[0,"straddle_hit_status"] = straddle_hit_status
        result_df.loc[0,"straddle_maxMTM"] = straddle_maxMTM
        result_df.loc[0,"straddle_minMTM"] = straddle_minMTM
        result_df.loc[0,"straddle_PnL"] = straddle_PnL
        return result_df
    

    
# Create an instance of the Straddle class with custom values
# obj = Straddle(merged_df = merged_df ,date='2020-05-05',
#                              exp_period='currWeek_exp_dt', underlying='BANKNIFTY',
#                              start_time='09:15', entry_time='09:20', exit_time='15:15', end_time='15:20',
#                              entry_side='sell', OTM_points=100,
#                              straddle_SL_pct=0.2, straddle_tgt_pct=0.8)


"""Runnign loop for all dates"""
result_df_all = pd.DataFrame(columns=['date', 'straddle_close', 'straddle_entryPrice', 'straddle_hit_status', 'straddle_minMTM', 'straddle_maxMTM', 'straddle_PnL'])

for date_dt in unique_dates:
    print(date_dt)

    
    try:
        obj = Straddle(merged_df = merged_df ,date=date_dt,
                                    exp_period='currWeek_exp_dt', underlying='BANKNIFTY',
                                    start_time='09:15', entry_time='09:20', exit_time='15:15', end_time='15:20',
                                    entry_side='sell', OTM_points=100,
                                    straddle_SL_pct=0.2, straddle_tgt_pct=0.8)
        
        result_row_df = obj.get_result_row()
        result_df_all = pd.concat([result_df_all, result_row_df], ignore_index=True)

    except Exception as e:
        print(f"Some Error Occured for the {date_dt}, {e}")

print(result_df_all)

 # %%

