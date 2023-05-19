rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'],format='%Y%m%d').dt.date
rel_PE_df['PEdate'] = pd.to_datetime(rel_PE_df['PEdate'])
rel_PE_df['PEdate'] = rel_PE_df['PEdate'].astype('str')
PEdatetime = pd.to_datetime(rel_PE_df['PEdate'] + ' ' + rel_PE_df['PEtime'], format='%Y-%m-%d %H:%M')
rel_PE_df.set_index(PEdatetime,inplaPE=True)
rel_PE_df=rel_PE_df.loc[date]
rel_PE_df.drop(columns=['PEdate','PEtime'],inplaPE=True)




#Creating  CE_entryPrice column
PE_entryPriceValue = rel_PE_df.loc[rel_PE_df.index.time == entry_time_dt ]['PEclose'].values[0]

rel_PE_df['PEentryPrice'] = np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEentryPrice'] = PE_entryPriceValue

#Creating PEstoploss
rel_PE_df['PEstoploss'] =np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEstoploss'] = PE_entryPriceValue*(1+Sl_pct)

#Creating target
rel_PE_df['PEtarget'] = np.NaN
rel_PE_df.loc[rel_PE_df.index.time > entry_time_dt, 'PEtarget'] = PE_entryPriceValue*(1 - tgt_pct)


#Creating PE_SL_hit
rel_PE_df['PE_SLhit'] = np.where(rel_PE_df['PEhigh'] >= rel_PE_df['PEstoploss'], 1, 0)

#Creating PE_Tgthit
rel_PE_df['PE_Tgthit'] = np.where(rel_PE_df['PElow'] <= rel_PE_df['PEtarget'], 1, 0)


#--->calculating PEhitstatus
#Creating hitType column whether SL/TGT/Squreoff
condition1 = rel_PE_df['PE_SLhit'] == 1
condition2 = rel_PE_df['PE_Tgthit']==1
condition3 = rel_PE_df.index.time == exit_time_dt



rel_PE_df['PEhitstatus'] = ''
rel_PE_df.loc[condition1, 'PEhitstatus'] = 'SL_hit'
rel_PE_df.loc[condition2, 'PEhitstatus'] = 'TGThit'
rel_PE_df.loc[condition3, 'PEhitstatus'] = 'squareoff'


#--->Calcuating PEexitPrice column
rel_PE_df['PEexitPrice'] = np.NaN
rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'SL_hit','PEexitPrice'] = rel_PE_df['PEstoploss']
rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'TGThit','PEexitPrice'] = rel_PE_df['PEtarget']
rel_PE_df.loc[rel_PE_df['PEhitstatus'] == 'squareoff','PEexitPrice'] = rel_PE_df['PEclose']

#--->Calcuating PE_MTM column
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_MTM'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PEclose'], np.nan)



#--->Calcuating PE_highMTM (entryPrice-low)
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_highMTM'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PElow'], np.nan)


#--->Calcuating PE_maxMTM
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_maxMTM'] = np.where(condition,rel_PE_df['PE_highMTM'].cummax(), np.nan)


#--->Calcuating PE_lowMTM  (entryPrice-high)
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_lowMTM'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PEhigh'], np.nan)

#--->Calcuating PE_minMTM
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_minMTM'] = np.where(condition,rel_PE_df['PE_lowMTM'].cummin(), np.nan)


#--->Calcuating PE_PnL column
condition = (rel_PE_df.index.time >= entry_time_dt) & (rel_PE_df.index.time <= end_time_dt)
rel_PE_df['PE_PnL'] = np.where(condition, rel_PE_df['PEentryPrice'] - rel_PE_df['PEexitPrice'], np.nan)
print(rel_PE_df.tail(30))