
# %%=======================================================
from merged_df import MergedDataFrame

obj = MergedDataFrame(underlying='BANKNIFTY')
merged_df1 = obj.get_merged_df()
print(obj.guide())



# %%============================================================
from straddle_df import Straddle
obj2 = Straddle(merged_df=merged_df1,date='2022-03-10', exp_period='currWeek_exp_dt', underlying='BANKNIFTY',
                             start_time='09:15', entry_time='09:30', exit_time='15:15', end_time='15:20',
                             entry_side='sell', OTM_points=100,
                             straddle_SL_pct=0.2, straddle_tgt_pct=0.8)
# print(obj.guide())
obj2.straddle_df
# %%


