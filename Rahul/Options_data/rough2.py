import numpy as np
import pandas as pd

# Set the display width option
# date = '2022-03-10'      
# date_dt = pd.to_datetime(date).date()



df = pd.read_csv('C:\\keshav\\Rahul\\Options_data\\NIFTY & BANKNIFTY (Jan 2020 to 19 Dec 2022)\\NIFTY & BANKNIFTY Spot Indices (Jan 2020 to 19 Dec 2022)\\BANKNIFTY.csv',header=None)

df.rename(columns={0:'date'},inplace=True)
df=pd.to_datetime(df['date'],format='%Y%m%d')

x = df.unique()[0]
x_str = x.strftime('%Y-%m-%d')
print(type(x_str))

# df =df.apply(lambda x: x.strftime('%Y-%m-%d'))
# df_lst= df.values   # list created


# print(list(df_lst).unique())


# unique_lst = []
# for item in df_lst:
#     if item not in unique_lst:
#         item = pd.to_datetime(item).date()
#         unique_lst.append(item)


# print(unique_lst)