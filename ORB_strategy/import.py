from packages import ORB_stg as os
import numpy as np
import pandas as pd
#Read file
df = pd.read_csv("C:\\keshav\\Intraday_1_minute\\2022\\2022 APR BNF.txt",header=None,index_col=False)

df.rename(columns={

                    0:'index',
                    1 : 'date',
                    2: 'time',
                    3: 'open',
                    4:'high',
                    5:'low',
                    6:'close'
    },inplace=True)

df = df.iloc[:, 0:-2]
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

#input list of all dates receiving 
input_list = df['date'].dt.date.astype('str').unique()


output_df = pd.DataFrame()
for input_values in input_list:
    obj = os.Orbstg(date = input_values ,path="C:\\keshav\\Intraday_1_minute\\2022\\2022 APR BNF.txt",exit_time=pd.Timestamp('15:15:00').time())
    report = obj.report_grp()
    obj.to_csv()
    output_df = pd.concat([output_df,report])
print(output_df)
