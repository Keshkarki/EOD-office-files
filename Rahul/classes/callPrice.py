
# %%
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# %%
# Making call price class

class CallPrice:
    """ Making call price class"""

    def __init__(self, underlying, entryDaysFromExpiry, exitDaysFromExpiry, entryTime, exitTime, strikeDiff, OTM_points):

        self.underlying = underlying
        self.entryDaysFromExpiry = entryDaysFromExpiry
        self.exitDaysFromExpiry = exitDaysFromExpiry
        self.entryTime = entryTime
        self.exitTime = exitTime
        self.strikeDiff = strikeDiff

        self.underlyingStrikeDiff = 100 if underlying == 'BANKNIFTY' else 50
        self.OTM_points = OTM_points


    def main_dataframe(self):
        path = "C:\\keshav\\Rahul\\BankniftyNifty\\Weekly_exp_dates.csv"
        df = pd.read_csv(path,usecols=['Exp_date'])
        df['expDateDt'] = pd.to_datetime(df['Exp_date'],format='%d-%b-%y')
        df['entry_date'] = df['expDateDt'] - pd.Timedelta(days=self.entryDaysFromExpiry)      #so we can have time delta
        df['entry_date'] = df['entry_date'].astype('str')   #so we can concat time with it
        df['entryDt'] = df['entry_date']+' '+self.entryTime
        df['entryDt'] =  pd.to_datetime(df['entryDt'])
        df['date'] = df['entryDt'].dt.date
        df['time'] = df['entryDt'].dt.date
        df.set_index('entryDt',inplace=True)
        df = df[['expDateDt', 'date','time']]
        self.df1 = df
        return self.df1


    def underlying_datafrme(self):
        path = f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\{self.underlying}.csv"
        df = pd.read_csv(path, header=None)

        df.rename(columns={
                    0   : 'date',
                    1   : 'time',
                    2   : 'open',
                    3   : 'high',
                    4   : 'low',
                    5   : 'close'
},inplace=True)

        df['date'] = pd.to_datetime(df['date'],format='%Y%m%d').dt.date.astype(str)
        df['datetime'] = df['date'] + ' ' + df['time']
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime',inplace=True)
        self.df2 = df
        return self.df2

    def merge_df_method(self):
        merged_df = pd.merge(self.main_dataframe(),self.underlying_datafrme()['close'], left_index=True,right_index=True, how='left')

        merged_df['BANKNIFTY_price'] = merged_df['close']

        #column --> CE_strike and PE_strike
        merged_df['CE_strike'] = (round(merged_df['BANKNIFTY_price']/self.underlyingStrikeDiff)*self.underlyingStrikeDiff + self.strikeDiff).astype(int)
        merged_df['PE_strike'] = (round(merged_df['BANKNIFTY_price']/self.underlyingStrikeDiff)*self.underlyingStrikeDiff - self.strikeDiff).astype(int)

        #adding relevent entryDate by shifting above one
        merged_df.reset_index(inplace=True)
        merged_df.insert(0,'relventExpiryDt',merged_df['entryDt'].shift(-1))
        merged_df.set_index('entryDt',inplace=True)
        self.merge_df = merged_df
        return self.merge_df

    def symbol_date(self):
        merged_df= self.merge_df_method()
        return merged_df['relventExpiryDt'].dt.strftime('%y%m%d')
    
    def call_price(self):
        merge_df = self.merge_df_method()
        strike_priceCE = merge_df['CE_strike'].astype(str)
        merge_df['symbolCE'] = self.underlying+self.symbol_date()+strike_priceCE+'CE'

        #adding year column for searching symbol  #doubt which year to take
        # merge_df['year']=merge_df['expDateDt'].dt.year.astype(str)
        merge_df.insert(0, 'year', merge_df.index.year.astype(str))
        merge_df['CEprice'] = np.NaN
        print(merge_df.columns)

        for i, row in merge_df.iterrows():
            ce_symbol = row['symbolCE']
            ce_year = row['year']
            dt = row.name

            try:
                rel_CE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{ce_year}\\{self.underlying} Options\\{ce_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['CEdate', 'CEtime', 'CEopen', 'CEhigh', 'CElow', 'CEclose'])

                rel_CE_df['CEdate'] = pd.to_datetime(rel_CE_df['CEdate'],format='%Y%m%d').dt.date.astype(str)
                rel_CE_df['datetime'] = rel_CE_df['CEdate'] + ' ' + rel_CE_df['CEtime']
                rel_CE_df['datetime'] = pd.to_datetime(rel_CE_df['datetime'])
                rel_CE_df.set_index('datetime',inplace=True)


                if dt in rel_CE_df.index:
                    # # Update the CEprice column in the original DataFrame
                    CEpriceValue = rel_CE_df.loc[dt, 'CEclose']
                    merge_df.loc[dt, 'CEprice'] = CEpriceValue
                else:
                    # df.loc[dt, 'CEprice'] = np.NaN
                    nearest_loc_index = rel_CE_df.index.searchsorted(dt).item()
                    nearest_loc_index = nearest_loc_index -1  #since indexing starts from 1

                    CEpriceValue = rel_CE_df.iloc[nearest_loc_index]['CEclose']
                    merge_df.loc[dt, 'CEprice'] = CEpriceValue

            except FileNotFoundError:
                print(f"File not found for {ce_symbol} in {ce_year}")
                pass


        return merge_df
            


    def put_price(self):
        merge_df = self.call_price()
        strike_pricePE = merge_df['PE_strike'].astype(str)
        merge_df['symbolPE'] = self.underlying+self.symbol_date()+strike_pricePE+'PE'

        merge_df['PEprice'] = np.NaN

        for i, row in merge_df.iterrows():
            Pe_symbol = row['symbolPE']
            Pe_year = row['year']
            dt = row.name

            try:
                rel_PE_df = pd.read_csv(f"C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Options (Jan 2020 to 19 Dec 2022)\\{Pe_year}\\{self.underlying} Options\\{Pe_symbol}.csv",header=None, usecols=[0, 1, 2, 3, 4, 5], names=['PEdate', 'PEtime', 'PEopen', 'PEhigh', 'PElow', 'PEclose'])

                rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date.astype(str)
                rel_PE_df['datetime'] = rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime']
                rel_PE_df['datetime'] = pd.to_datetime(rel_PE_df['datetime'])
                rel_PE_df.set_index('datetime',inplace=True)


                if dt in rel_PE_df.index:
                    # # Update the PEprice column in the original DataFrame
                    PEpriceValue = rel_PE_df.loc[dt, 'PEclose']
                    merge_df.loc[dt, 'PEprice'] = PEpriceValue
                else:
                    # df.loc[dt, 'PEprice'] = np.NaN
                    nearest_loc_index = rel_PE_df.index.searchsorted(dt).item()
                    nearest_loc_index = nearest_loc_index -1  #sinPe indexing starts from 1

                    PEpriceValue = rel_PE_df.iloc[nearest_loc_index]['PEclose']
                    merge_df.loc[dt, 'PEprice'] = PEpriceValue

            except FileNotFoundError:
                print(f"File not found for {Pe_symbol} in {Pe_year}")
                pass


        merge_df.rename(columns = {
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

        merge_df.drop(columns=['Entry_date','Entry_time','Entry_expDateDt'],inplace=True)
        merge_df['Entry_relventExpiryDt'] = merge_df['Entry_relventExpiryDt'].fillna(method='ffill')
#Note by shifring entryDt last value is NaT hence doing ffill

obj = CallPrice(underlying='BANKNIFTY', entryDaysFromExpiry=0, exitDaysFromExpiry=0, entryTime='15:15', exitTime='15:15', strikeDiff=0, OTM_points=100)
# obj.main_dataframe()
# obj.underlying_datafrme()
# obj.merge_df()
# obj.symbol_date()
# obj.call_price()
obj.put_price()





# %%
