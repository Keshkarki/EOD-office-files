
import numpy as np
import pandas as pd
import os

niftySingle = pd.read_csv('niftySingle.csv', usecols=['Date', 'Close'], index_col='Date')
niftySingle.rename(columns={'Close' : 'niftyPrice'},inplace=True)
niftySingle.insert(0,'company', 'nifty50')
niftySingle

# ## listing all companies
list_of_companies = os.listdir('C:\\keshav\\Navneet_sir_all\\Nifty50_dashboard_levels\\Nifty50_Data')
list_of_companies

# ## setting up one comapny

for company in list_of_companies[0:2]:
    print(company)

    df = pd.read_csv(f'C:\\keshav\\Navneet_sir_all\\Nifty50_dashboard_levels\\Nifty50_Data\\{company}', usecols=['Date','Close'], index_col='Date')
    df.rename(columns={'Close' : 'price'}, inplace=True)
    company_name = f"{company.split('.')[0]}"
    df.insert(0, 'company', company_name)

    niftySingle = pd.merge(niftySingle, df, left_index=True, right_index=True, how='inner', suffixes=(f'_{company_name}', f'_{company_name}'))
    niftySingle['ratio'] = niftySingle['niftyPrice'] / niftySingle['price']
    niftySingle['mean'] = niftySingle['ratio'].mean()
    niftySingle['std'] = niftySingle['ratio'].std()
    print(niftySingle)


