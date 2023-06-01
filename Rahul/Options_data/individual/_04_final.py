
# %%
import numpy as np
import pandas as pd
import time

from _01_merged_df import MergedDataFrame
obj = MergedDataFrame(underlying='BANKNIFTY')
merged_df = obj.get_merged_df()
unique_dates = obj.get_unique_dates()

# %%

start_time = time.time()
class Individual:
    def __init__(self,merged_df, date, exp_period, underlying,
                 start_time, entry_time, exit_time, end_time,
                 entry_side, OTM_points,
                 individual_SL_pct, individual_tgt_pct):
        
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
        self.individual_SL_pct = individual_SL_pct        #0.2 -> 20%
        self.individual_tgt_pct =individual_tgt_pct  #0.8 --> 80%


        #conversion
        self.date_dt = pd.to_datetime(date).date()
        self.entry_time_dt = pd.to_datetime(self.entry_time).time()
        self.exit_time_dt = pd.to_datetime(self.exit_time).time()
        self.end_time_dt = pd.to_datetime(self.end_time).time()

        #for filtering and adding hit status between  index which is first hit and exit_timestamp
        self.datetime_str = f'{self.date} {self.exit_time}'
        self.exit_timestamp = pd.to_datetime(self.datetime_str)

        #for function working to call
        self.result_df_all()


    def result_df_all(self):

        # calcualting strikr prices  and symbol
        atm_strike_price = self.merged_df.loc[(self.merged_df.index.time == self.entry_time_dt) & (self.merged_df.index.date == self.date_dt), 'ATMStrPr'].values[0]
        ce_strike_price = round(atm_strike_price + self.OTM_points)
        pe_strike_price = round(atm_strike_price - self.OTM_points)

        self.merged_df['CE_strike_price'] = ce_strike_price
        self.merged_df['PE_strike_price'] = pe_strike_price

        self.CE_stp = str(ce_strike_price)
        self.PE_stp = str(pe_strike_price)
        # print(self.CE_stp)
        # print(self.PE_stp)



        # locating expiry date as per input
        result = self.merged_df.loc[(self.merged_df.index.time == self.entry_time_dt) & (self.merged_df.index.date == self.date_dt)][self.exp_period]
        result = result.values[0]
        date = pd.to_datetime(result)
        formatted_date = date.strftime('%y%m%d')
        self.exp_date = formatted_date
        # print(self.exp_date)
        
            # Generate symbols
        self.ce_symbol = f"{self.underlying}{self.exp_date}{self.CE_stp}CE"
        self.pe_symbol = f"{self.underlying}{self.exp_date}{self.PE_stp}PE"



        #  rel_CE_df 
        try:
            path = f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.datestr}\\{self.underlying} Options\\{self.ce_symbol}.csv"
            
            rel_CE_df = pd.read_csv(path,header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

            rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'],format='%Y%m%d').dt.date
            rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'])
            rel_CE_df['CEdate'] = rel_CE_df['CEdate'].astype('str')
            CEdatetime = pd.to_datetime(rel_CE_df['CEdate'] + ' ' + rel_CE_df['CEtime'], format='%Y-%m-%d %H:%M')
            rel_CE_df.set_index(CEdatetime,inplace=True)
            rel_CE_df=rel_CE_df.loc[self.date]
            self.rel_CE_df = rel_CE_df
     
        except:
            print('File path is not valid')



        #Creating  CE_entryPrice column
        CE_entryPriceValue = self.rel_CE_df.loc[self.rel_CE_df.index.time == self.entry_time_dt ]['CEclose'].values[0]

        self.rel_CE_df['CE_entryPrice'] = np.NaN
        self.rel_CE_df.loc[self.rel_CE_df.index.time > self.entry_time_dt, 'CE_entryPrice'] = CE_entryPriceValue



        #Creating CE_stoploss
        self.rel_CE_df['CE_stoploss'] =np.NaN

        if self.entry_side =='sell':
            self.rel_CE_df.loc[self.rel_CE_df.index.time > self.entry_time_dt, 'CE_stoploss'] = CE_entryPriceValue*(1+self.individual_SL_pct)

        else:
            self.rel_CE_df.loc[self.rel_CE_df.index.time > self.entry_time_dt, 'CE_stoploss'] = CE_entryPriceValue*(1- self.individual_SL_pct)      




        #Creating target
        self.rel_CE_df['CE_tgt'] = np.NaN

        if self.entry_side == 'sell':
            self.rel_CE_df.loc[self.rel_CE_df.index.time > self.entry_time_dt, 'CE_tgt'] = CE_entryPriceValue*(1 - self.individual_tgt_pct)

        else:
            self.rel_CE_df.loc[self.rel_CE_df.index.time > self.entry_time_dt, 'CE_tgt'] = CE_entryPriceValue*(1 + self.individual_tgt_pct)

            

        # #Creating CE_SL_hit
        self.rel_CE_df['CE_SLhit'] = np.where(self.rel_CE_df['CEhigh'] >= self.rel_CE_df['CE_stoploss'], 1, 0)



        #Creating CE_Tgthit
        self.rel_CE_df['CE_Tgthit'] = np.where(self.rel_CE_df['CElow'] <= self.rel_CE_df['CE_tgt'], 1, 0)


        #--->calculating CE_hit_status
        #Creating hitType column whether SL/TGT/Squreoff
        condition1 = self.rel_CE_df['CE_SLhit'] == 1
        condition2 = self.rel_CE_df['CE_Tgthit']==1
        condition3 = self.rel_CE_df.index.time == self.exit_time_dt

        self.rel_CE_df['CE_hit_status'] = ''
        self.rel_CE_df.loc[condition1, 'CE_hit_status'] = 'SL_hit'
        self.rel_CE_df.loc[condition2, 'CE_hit_status'] = 'TGThit'
        self.rel_CE_df.loc[condition3, 'CE_hit_status'] = 'squareoff'



        first_non_null = self.rel_CE_df[self.rel_CE_df['CE_hit_status'] != '']['CE_hit_status'].iloc[0]
        self.rel_CE_df['CE_hit_status'] = np.where(self.rel_CE_df['CE_hit_status'] != '', first_non_null,'')

        mask = self.rel_CE_df['CE_hit_status'] == first_non_null
        index_position = self.rel_CE_df.index[mask].tolist()[0]

        self.rel_CE_df.loc[((self.rel_CE_df.index > index_position) & (self.rel_CE_df.index < self.exit_timestamp)), 'CE_hit_status'] = first_non_null


        # #--->Calcuating CE_exitPrice column
        self.rel_CE_df['CE_exitPrice'] = np.NaN
        self.rel_CE_df.loc[self.rel_CE_df['CE_hit_status'] == 'SL_hit','CE_exitPrice'] = self.rel_CE_df['CE_stoploss']
        self.rel_CE_df.loc[self.rel_CE_df['CE_hit_status'] == 'TGThit','CE_exitPrice'] = self.rel_CE_df['CE_tgt']
        self.rel_CE_df.loc[self.rel_CE_df['CE_hit_status'] == 'squareoff','CE_exitPrice'] = self.rel_CE_df['CEclose']

        #--->Calcuating CE_MTM column
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CE_MTM'] = np.where(condition, self.rel_CE_df['CE_entryPrice'] - self.rel_CE_df['CEclose'], np.nan)

        #--->Calcuating CE_highMTM (entryprice-low)
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CE_highMTM'] = np.where(condition, self.rel_CE_df['CE_entryPrice'] - self.rel_CE_df['CElow'], np.nan)

        #--->Calcuating CE_maxMTM
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CE_maxMTM'] = np.where(condition,np.where(self.rel_CE_df['CE_highMTM'].cummax() > 0 ,self.rel_CE_df['CE_highMTM'].cummax() ,np.nan),np.nan)

        #--->Calcuating CElowMTM  (entryprice-high)
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CElowMTM'] = np.where(condition, self.rel_CE_df['CE_entryPrice'] - self.rel_CE_df['CEhigh'], np.nan)

        #--->Calcuating CE_minMTM
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CE_minMTM'] = np.where(condition,self.rel_CE_df['CElowMTM'].cummin(), np.nan)

        #--->Calcuating CE_PnL column
        condition = (self.rel_CE_df.index.time >= self.entry_time_dt) & (self.rel_CE_df.index.time <= self.end_time_dt)
        self.rel_CE_df['CE_PnL'] = np.where(condition, self.rel_CE_df['CE_entryPrice'] - self.rel_CE_df['CE_exitPrice'], np.nan)
    


        # rel_PE_df ========================================================

        try:
            path = f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{self.datestr}\\{self.underlying} Options\\{self.pe_symbol}.csv"
            rel_PE_df = pd.read_csv(path,header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])
            rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date
            rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'])
            rel_PE_df['PEdate'] = rel_PE_df['PEdate'].astype('str')

            PEdatetime = pd.to_datetime(rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime'], format='%Y-%m-%d %H:%M')
            rel_PE_df.set_index(PEdatetime,inplace=True)

            rel_PE_df=rel_PE_df.loc[self.date]
            self.rel_PE_df = rel_PE_df
            # print(self.rel_PE_df)
        
        except:
            print('file path is not valid')


        #Creating  PE_entryPrice column
        PE_entryPriceValue = self.rel_PE_df.loc[self.rel_PE_df.index.time == self.entry_time_dt ]['PEclose'].values[0]

        self.rel_PE_df['PE_entryPrice'] = np.NaN
        self.rel_PE_df.loc[self.rel_PE_df.index.time > self.entry_time_dt, 'PE_entryPrice'] = PE_entryPriceValue



        #Creating CE_stoploss
        self.rel_PE_df['PE_stoploss'] =np.NaN

        if self.entry_side =='sell':
            self.rel_PE_df.loc[self.rel_PE_df.index.time > self.entry_time_dt, 'PE_stoploss'] = PE_entryPriceValue*(1+self.individual_SL_pct)

        else:
            self.rel_PE_df.loc[self.rel_PE_df.index.time > self.entry_time_dt, 'PE_stoploss'] = PE_entryPriceValue*(1- self.individual_SL_pct)      




        #Creating target
        self.rel_PE_df['PE_tgt'] = np.NaN

        if self.entry_side == 'sell':
            self.rel_PE_df.loc[self.rel_PE_df.index.time > self.entry_time_dt, 'PE_tgt'] = PE_entryPriceValue*(1 - self.individual_tgt_pct)

        else:
            self.rel_PE_df.loc[self.rel_PE_df.index.time > self.entry_time_dt, 'PE_tgt'] = PE_entryPriceValue*(1 + self.individual_tgt_pct)

            

        # #Creating PE_SL_hit
        self.rel_PE_df['PE_SLhit'] = np.where(self.rel_PE_df['PEhigh'] >= self.rel_PE_df['PE_stoploss'], 1, 0)

        #Creating PE_Tgthit
        self.rel_PE_df['PE_Tgthit'] = np.where(self.rel_PE_df['PElow'] <= self.rel_PE_df['PE_tgt'], 1, 0)


        #--->calculating PE_hit_status
        #Creating hitType column whether SL/TGT/Squreoff
        condition1 = self.rel_PE_df['PE_SLhit'] == 1
        condition2 = self.rel_PE_df['PE_Tgthit']==1
        condition3 = self.rel_PE_df.index.time == self.exit_time_dt

        self.rel_PE_df['PE_hit_status'] = ''
        self.rel_PE_df.loc[condition1, 'PE_hit_status'] = 'SL_hit'
        self.rel_PE_df.loc[condition2, 'PE_hit_status'] = 'TGThit'
        self.rel_PE_df.loc[condition3, 'PE_hit_status'] = 'squareoff'


        first_non_null = self.rel_PE_df[self.rel_PE_df['PE_hit_status'] != '']['PE_hit_status'].iloc[0]
        self.rel_PE_df['PE_hit_status'] = np.where(self.rel_PE_df['PE_hit_status'] != '', first_non_null,'')

        mask = self.rel_PE_df['PE_hit_status'] == first_non_null
        index_position = self.rel_PE_df.index[mask].tolist()[0]

        self.rel_PE_df.loc[((self.rel_PE_df.index > index_position) & (self.rel_PE_df.index < self.exit_timestamp)), 'PE_hit_status'] = first_non_null


        # #--->Calcuating PE_exitPrice column
        self.rel_PE_df['PE_exitPrice'] = np.NaN
        self.rel_PE_df.loc[self.rel_PE_df['PE_hit_status'] == 'SL_hit','PE_exitPrice'] = self.rel_PE_df['PE_stoploss']
        self.rel_PE_df.loc[self.rel_PE_df['PE_hit_status'] == 'TGThit','PE_exitPrice'] = self.rel_PE_df['PE_tgt']
        self.rel_PE_df.loc[self.rel_PE_df['PE_hit_status'] == 'squareoff','PE_exitPrice'] = self.rel_PE_df['PEclose']

        #--->Calcuating PE_MTM column
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PE_MTM'] = np.where(condition, self.rel_PE_df['PE_entryPrice'] - self.rel_PE_df['PEclose'], np.nan)

        #--->Calcuating PE_highMTM (entryprice-low)
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PE_highMTM'] = np.where(condition, self.rel_PE_df['PE_entryPrice'] - self.rel_PE_df['PElow'], np.nan)

        #--->Calcuating PE_maxMTM
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PE_maxMTM'] = np.where(condition,np.where(self.rel_PE_df['PE_highMTM'].cummax() > 0 ,self.rel_PE_df['PE_highMTM'].cummax() ,np.nan),np.nan)

        #--->Calcuating PElowMTM  (entryprice-high)
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PElowMTM'] = np.where(condition, self.rel_PE_df['PE_entryPrice'] - self.rel_PE_df['PEhigh'], np.nan)

        #--->Calcuating PE_minMTM
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PE_minMTM'] = np.where(condition,self.rel_PE_df['PElowMTM'].cummin(), np.nan)

        #--->Calcuating PE_PnL column
        condition = (self.rel_PE_df.index.time >= self.entry_time_dt) & (self.rel_PE_df.index.time <= self.end_time_dt)
        self.rel_PE_df['PE_PnL'] = np.where(condition, self.rel_PE_df['PE_entryPrice'] - self.rel_PE_df['PE_exitPrice'], np.nan)



        # #getting last row close values 
        date = self.rel_CE_df.index.date[0]

        CEclose = self.rel_CE_df['CEclose'][self.rel_CE_df['CEclose'].last_valid_index()]

        CE_entryPrice = self.rel_CE_df['CE_entryPrice'][self.rel_CE_df['CE_entryPrice'].last_valid_index()]

        non_blank_list = self.rel_CE_df['CE_hit_status'][self.rel_CE_df['CE_hit_status'].values !='']

        CE_hit_status = non_blank_list[non_blank_list.last_valid_index()]

        try:
            CE_maxMTM = self.rel_CE_df['CE_maxMTM'][self.rel_CE_df['CE_maxMTM'].last_valid_index()]

        except:
            CE_maxMTM = 0

        try:
            CE_minMTM = self.rel_CE_df['CE_minMTM'][self.rel_CE_df['CE_minMTM'].last_valid_index()]

        except:
           CE_minMTM = 0

        CE_PnL = self.rel_CE_df['CE_PnL'][self.rel_CE_df['CE_PnL'].last_valid_index()]


 # FOR PE

        PEclose = self.rel_PE_df['PEclose'][self.rel_PE_df['PEclose'].last_valid_index()]

        PE_entryPrice = self.rel_PE_df['PE_entryPrice'][self.rel_PE_df['PE_entryPrice'].last_valid_index()]

        non_blank_list = self.rel_PE_df['PE_hit_status'][self.rel_PE_df['PE_hit_status'].values !='']

        PE_hit_status = non_blank_list[non_blank_list.last_valid_index()]

        try:
            PE_maxMTM = self.rel_PE_df['PE_maxMTM'][self.rel_PE_df['PE_maxMTM'].last_valid_index()]

        except:
            PE_maxMTM = 0

        try:
            PE_minMTM = self.rel_PE_df['PE_minMTM'][self.rel_PE_df['PE_minMTM'].last_valid_index()]

        except:
           PE_minMTM = 0

        PE_PnL = self.rel_PE_df['PE_PnL'][self.rel_PE_df['PE_PnL'].last_valid_index()]


        result_df = pd.DataFrame(columns=['date','CEclose','CE_entryPrice', 'CE_hit_status', 'CE_minMTM','CE_maxMTM','CE_PnL','PEclose','PE_entryPrice', 'PE_hit_status', 'PE_minMTM','PE_maxMTM','PE_PnL','Total_PnL'])



        result_df.loc[0,"date"] = date
        result_df.loc[0,"CEclose"] = CEclose
        result_df.loc[0,"CE_entryPrice"] = CE_entryPrice
        result_df.loc[0,"CE_hit_status"] = CE_hit_status
        result_df.loc[0,"CE_maxMTM"] = CE_maxMTM
        result_df.loc[0,"CE_minMTM"] = CE_minMTM
        result_df.loc[0,"CE_PnL"] = CE_PnL

        result_df.loc[0,"PEclose"] = PEclose
        result_df.loc[0,"PE_entryPrice"] = PE_entryPrice
        result_df.loc[0,"PE_hit_status"] = PE_hit_status
        result_df.loc[0,"PE_maxMTM"] = PE_maxMTM
        result_df.loc[0,"PE_minMTM"] = PE_minMTM
        result_df.loc[0,"PE_PnL"] = PE_PnL

        result_df.loc[0,"Total_PnL"] = CE_PnL + PE_PnL

        self.result_df = result_df
    

   
# Create an instance of the individual class with custom values
# obj = Individual(merged_df = merged_df,date='2020-05-07',
#                              exp_period='currWeek_exp_dt', underlying='BANKNIFTY',
#                              start_time='09:15', entry_time='09:20', exit_time='15:15', end_time='15:20',
#                              entry_side='sell', OTM_points=100,
#                              individual_SL_pct=0.2, individual_tgt_pct=0.8)


"""Runnign loop for all dates"""
result_df_all = pd.DataFrame(columns=['date','CEclose','CE_entryPrice', 'CE_hit_status', 'CE_minMTM','CE_maxMTM','CE_PnL','PEclose','PE_entryPrice', 'PE_hit_status', 'PE_minMTM','PE_maxMTM','PE_PnL','Total_PnL'])

for date_dt in unique_dates:
    try:
        obj = Individual(merged_df = merged_df ,date=date_dt,
                                    exp_period='currWeek_exp_dt', underlying='BANKNIFTY',
                                    start_time='09:15', entry_time='09:20', exit_time='15:15', end_time='15:20',
                                    entry_side='sell', OTM_points=100,
                                    individual_SL_pct=0.2, individual_tgt_pct=0.8)
        
        result_row_df = obj.result_df
        result_df_all = pd.concat([result_df_all, result_row_df], ignore_index=True)

    except Exception as e:
        print(f"Some Error Occured for the {date_dt}, {e}")

print(result_df_all)

end_time = time.time()
total_time = end_time - start_time
print(f" Total Time take : {total_time}")

 # %%





