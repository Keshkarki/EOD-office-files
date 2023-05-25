import os
import pandas as pd
# pd.set_option('display.max_rows',None)

# folder_path = "C:\\keshav\\Navneet_datascrap\\dataforbacktesting"

folder_path = "C:\\keshav\\Navneet_datascrap\\2023,05,24\\all_files"
file_list = os.listdir(folder_path)
file_list


def file_read():
    """ If new files added delete testing1 and finalTestingFile csvs and run function once"""
    if os.path.exists('testing1.csv'):
        return pd.read_csv('testing1.csv')
        
    else:
        data = []
        for file_name in file_list:
            if file_name.endswith(".xlsx"):
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_excel(file_path, header=None)
                date = df.iloc[21, 3]
                NetRealizedPnL = df.iloc[25, 8]
                NetUnrealizedPnL = df.iloc[25, 14]
                TotalGL = df.iloc[25, 16]
                data.append([date, NetRealizedPnL, NetUnrealizedPnL, TotalGL])

        df_result = pd.DataFrame(data, columns=["Date", "NetRealizedPnL", "NetUnrealizedPnL", "TotalGL"])
        df_result.to_csv('testing1.csv', index=False)

        

df = file_read()

# df[['FromDate', 'ToDate']] = df['Date'].str.split(' to ', expand=True)
# df.drop(columns='Date',inplace=True)
# df = df[['FromDate','ToDate','NetRealizedPnL','NetUnrealizedPnL','TotalGL']]
# df['FromDate'] = pd.to_datetime(df['FromDate'],format='%d-%b-%Y')
# df['ToDate'] = pd.to_datetime(df['ToDate'],format='%d-%b-%Y')
# df = df.sort_values(by='FromDate', ascending=True)
# # df.to_csv('finalTestingFile.csv',index=False)
# print(df)
