
import pandas as pd
import numpy as np
import datetime as dt


class Orbstg:

    """
    This class will calculate daily PnL and MTM for Intraday data
    """

    def __init__(self,date=None,path=None,exit_time=None):
        self.exit_time = exit_time
        self.path=path
        self.date = date
        self.df = pd.DataFrame()
        self.grouped_df = pd.DataFrame()
        self.read_csv()
        self.open_df()
        self.calculating_range()
        self.apply_signal()
        self.get_trade_count()
        self.buy_methods()
        self.sell_methods()
        self.buy_method2()
        self.sell_method2()
        self.final_mtm()

        if self.exit_time is not None:
             self.exit_time = self.exit_time
        
        else:
             self.exit_time = pd.Timestamp('15:15:00').time()



    def read_csv(self):
        df = pd.read_csv(self.path,index_col=False,header=None)
        df = df.iloc[:,:7]
       
        df.rename(columns={
                    0:'index',
                    1 : 'date',
                    2: 'time',
                    3: 'open',
                    4:'high',
                    5:'low',
                    6:'close'
    },inplace=True)
        


        #pre setup str for concatenation further
        df['date'] = df['date'].astype('str')
        datetime = pd.to_datetime(df['date'] + ' ' + df['time'], format='%Y%m%d %H:%M')
        df.insert(1,'datetime',datetime) 
        df['date'] = pd.to_datetime(df['date'])
        df['time'] = pd.to_datetime(df['time'], format='%H:%M').dt.time
        df.set_index('datetime',inplace=True)


        #date filtered
        if self.date is not None :
            df = df.loc[self.date]

        #selecting market timing only
        df = df.between_time('09:16:00', '15:30:00')
        self.df = df

    #==>calculating open df
    def open_df(self):
        start_time = self.df.index[0]
        end_time = start_time + pd.Timedelta(minutes=15)
        open_df = self.df.loc[start_time:end_time]
        self.open_df = open_df


    def calculating_range(self):
        self.rangeHigh = self.open_df['high'].max()
        self.rangeLow = self.open_df['low'].min()

        self.df['rangeHigh'] = self.rangeHigh
        self.df['rangeLow'] = self.rangeLow
        self.df['range'] = self.df['rangeHigh'] - self.df['rangeLow']


    # Signal function
    def get_signal(self,row):
        if row['high'] > self.rangeHigh:
            return 'Buy'
        elif row['low'] < self.rangeLow:
            return 'Sell'
        else:
            return np.nan
    
    def apply_signal(self):
        self.df['signal'] = self.df.apply(self.get_signal,axis=1)
        self.df['tradePosition'] = self.df['signal'].fillna(method='ffill')
        # print(self.df.head(50))


    def get_trade_count(self):
        self.df['tradeCount'] = 0
        current_count = 0
        for i in range(len(self.df)):
            if pd.isnull(self.df['tradePosition'].iloc[i]):
                self.df.loc[self.df.index[i],'tradeCount'] = current_count
            else:
                if self.df['tradePosition'].iloc[i] != self.df['tradePosition'].iloc[i-1]:
                    current_count += 1
                self.df.loc[self.df.index[i],'tradeCount'] = current_count



        #intrade counts
        self.df['inTrade'] = np.where((self.df['tradeCount'] > 0) & (self.df['tradeCount'] <3), 1, 0)

        #entryCount
        # self.df['entryCount'] = np.where((self.df['date'] == self.df['date'].shift()) ,((self.df['tradeCount']!= self.df['tradeCount'].shift()) & self.df['inTrade']==1 , 1,0),0)
        # print(self.df.head(100))

        entry_condition = (self.df['date'] == self.df['date'].shift()) & (self.df['tradeCount'] != self.df['tradeCount'].shift()) & (self.df['inTrade'] == 1)
        entry_value = np.where(entry_condition, 1, 0)
        self.df['entryCount'] = entry_value



    def buy_methods(self):
        #==> BuyPrice
        self.df.loc[(self.df['tradePosition']=='Buy')&(self.df['inTrade'] ==1),'buyPrice'] = self.df['rangeHigh']

        #==>buySL
        condition1 = (self.df['inTrade'] == 1) & (self.df['tradePosition'] != 'Buy')
        condition2 = (self.df['inTrade'] == 1) & (self.df['tradePosition'] == 'Buy')
        self.df['buySL'] = np.where(condition1, np.NaN, np.where(condition2, self.df['rangeLow'], np.NaN))

        #==>butTarget
        # 20 % not fixed here variable
        condition = (self.df['tradePosition'] == 'Buy') & (self.df['inTrade'] == 1)
        self.df['buyTgt'] = np.where(condition, self.df['buyPrice'] + self.df['range'] * 0.02, np.NaN)
        # print(self.df.head(100))

    def sell_methods(self):
        self.df.loc[(self.df['tradePosition']=='Sell')&(self.df['inTrade'] ==1),'sellPrice'] = self.df['rangeLow']

        #==>sell sl
        condition1 = (self.df['inTrade'] == 1) & (self.df['tradePosition'] != 'Sell')
        condition2 = (self.df['inTrade'] == 1) & (self.df['tradePosition'] == 'Sell')
        self.df['sellSL'] = np.where(condition1, np.NaN, np.where(condition2, self.df['rangeHigh'], np.NaN))

        #==>sell target
        condition = (self.df['tradePosition'] == 'Sell') & (self.df['inTrade'] == 1)
        self.df['sellTgt'] = np.where(condition, self.df['sellPrice'] - self.df['range'] * 0.02, np.NaN)


    def buy_method2(self):

        self.df['buySLHit'] = np.where(self.df['low'] <= self.df['buySL'].shift(), 1, 0)
        self.df['buySLHit'] = np.where(
                                (self.df['tradePosition'].shift() == 'Buy') & (self.df['buySLHit'].shift() == 1), 1,
                            np.where((self.df['tradePosition'].shift() == 'Buy') & (self.df['inTrade'].shift() == 1),
                                    np.where(self.df['low'] <= self.df['buySL'].shift(), 1, 0),
                                    0))


        ## buy_tg hit
        self.df['buyTgtHit'] =  np.where(self.df['high'] >= self.df['buyTgt'].shift(), 1, 0)

        self.df['buyTgtHit'] = np.where(
                            (self.df['tradePosition'].shift() == 'Buy') & (self.df['buyTgtHit'].shift() == 1),
                            1,
                            np.where(
                                (self.df['tradePosition'].shift() == 'Buy') & (self.df['inTrade'].shift() == 1) & (self.df['entryCount'].shift() == 0),
                                1,
                                0))

    #buyTrade on
        self.df['buyTradeOn'] = np.where(self.df.index.time >= self.exit_time,0,
                                                                         np.where(
                                (self.df['tradePosition'] =='Buy')&(self.df['inTrade']==1)&(self.df['buySLHit']==0)&(self.df['buyTgtHit']==0),
                                1,0)
        )

        # print(self.df.head(50))


    #buy exit price
        self.df['buyExitPrice'] = np.where(
                                (self.df['buyTradeOn'].shift() == 1) & (self.df['buyTradeOn']==0),
                                np.where(
                                        (self.df['buySLHit']==1), self.df['buySL'].shift(),
                                        np.where(self.df['buyTgtHit']==1,self.df['buyTgt'],self.df['close'])
                                ),0)

    #buy MTM
        self.df['buyMTM'] = np.where(self.df['buyTradeOn' ]==1,self.df['close'] - self.df['buyPrice'],0)

    #buy PNL
        self.df['buyPnL'] = np.where(
                                    (self.df['buyTradeOn'].shift() == 1) & (self.df['buyTradeOn'] == 0),self.df['buyExitPrice'] - self.df['buyPrice'].shift(),0)


    def sell_method2(self):
        ## sellSLHit
        self.df['sellSLHit'] = np.where(self.df['high'] >= self.df['sellSL'].shift(),1,0)

        self.df['sellSLHit'] = np.where(
                                    (self.df['tradePosition'].shift() == 'Sell') & (self.df['sellSLHit'].shift() == 1),1,
                                    np.where(
                                            (self.df['tradePosition'].shift() == 'Sell') & (self.df['inTrade'].shift() == 1),
                                            np.where(self.df['high'] >= self.df['sellSL'].shift(),1,0),0 ))

        ## sellTgtHit
        self.df['sellTgtHit'] = np.where(self.df['low'] <= self.df['sellTgt'].shift(),1,0)

        self.df['sellTgtHit'] = np.where(
                                (self.df['tradePosition'].shift() == 'Sell') & (self.df['sellTgtHit'].shift() == 1),1,
                                    np.where(
                                                (self.df['tradePosition'].shift() == 'Sell') & (self.df['inTrade'].shift() == 1) & (self.df['entryCount'].shift() == 0),
                                                1,
                                                0))

    ## sell trade on


        self.df['sellTradeOn'] =  np.where(self.df.index.time >= self.exit_time,0,
                                                                np.where(
                                                            (self.df['tradePosition'] == "Sell") & (self.df['inTrade'] ==1) & (self.df['sellSLHit'] == 0) & (self.df['sellTgtHit'] ==0),1,0))


    ## sell exit price
        self.df['sellExitPrice'] = np.where(
                                    (self.df['sellTradeOn'].shift() ==1)&(self.df['sellTradeOn'] == 0),
                                        np.where(self.df['sellSLHit'] ==1,self.df['sellSL'],
                                                np.where(self.df['sellTgtHit'] ==1,self.df['sellTgt'],self.df['close'])),0)


    ## SEllMTM
        self.df['sellMTM'] = np.where(self.df['sellTradeOn'] ==1,self.df['sellPrice'] - self.df['close'],0)

    ## sellPnL
        self.df['sellPnL'] = np.where(
                                    (self.df['sellTradeOn'].shift() == 1) & (self.df['sellTradeOn'] == 0),
                                    self.df['sellPrice'].shift() - self.df['sellExitPrice'],
                                    0)


        ### buy max mtm 
    def final_mtm(self):

        self.df['buyMaxMTM'] = np.where(
            (self.df['tradePosition'] =="Buy") & (self.df['inTrade']==1) & (self.df['high'] - self.df['buyPrice'] > 0),(self.df['high'] - self.df['buyPrice']),0
        )

    ## buy min mtm
        self.df['buyMinMTM'] = np.where(
        (self.df['tradePosition'] =="Buy") & (self.df['inTrade']==1) & (self.df['high'] - self.df['buyPrice'] < 0),(self.df['high'] - self.df['buyPrice']),0)

    ## Sell max mtm
        self.df['sellMaxMTM'] = np.where(
        (self.df['tradePosition'] =="Sell") & (self.df['inTrade']==1) & (self.df['sellPrice'] - self.df['low'] > 0),(self.df['sellPrice'] - self.df['low']),0)

    ##  sell min mtm
        self.df['sellMinMTM'] = np.where(
        (self.df['tradePosition'] =="Sell") & (self.df['inTrade']==1) & (self.df['sellPrice'] - self.df['low'] < 0),(self.df['sellPrice'] - self.df['low']),0)

    #addinng new column totalPnL 
        self.df['totalPnl'] = self.df['buyPnL']+self.df['sellPnL']

    def to_csv(self):
        pass
        # self.df.to_csv('newformula.csv')


    def report_grp(self):
        grouped_df = self.df.groupby('date').agg({
                'buyPnL': 'sum',
                'sellPnL': 'sum',
                'totalPnl': 'sum',
                'buyMaxMTM': 'max',
                'buyMinMTM': 'min',
                'sellMaxMTM': 'max',
                'sellMinMTM': 'min'
            })

        print(grouped_df)
# #date format "month-date-year" ---> date = "04-07-2022"
# obj = Orbstg(date = "04-07-2022",path="C:\\keshav\\Intraday_1_minute\\2022\\2022 APR BNF.txt",exit_time = pd.Timestamp('15:15:00').time())



# obj.dataframe()
# obj.to_csv()    
# print(obj.report_grp()) 
# obj.open_df()
# obj.read_csv()
