import numpy as np
import pandas as pd

df1 = pd.read_csv("C:\\keshav\\Navneet_datascrap\\finalTestingFile1.csv")
# print(df1)


df2 = pd.read_csv("C:\\keshav\\Navneet_datascrap\\finalTestingFile2.csv")
# print(df2)


merged_df = pd.concat(df1,df2)
print(merged_df)