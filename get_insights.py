import pandas as pd
import sqlite3
import statsmodels.api as sm

def calc_demand_supply_ratio(df_rides, df_drivers, groupby_col):
    demand = df_rides.groupby(groupby_col).size().reset_index(name='rides_requested')
    supply = df_rides.dropna(subset=['driver_id']).groupby(groupby_col)['driver_id'].nunique().reset_index(name='active_drivers')
    
    ratio = pd.merge(demand, supply, on=groupby_col, how='left')
    ratio['active_drivers'].fillna(1, inplace=True)
    ratio['ds_ratio'] = ratio['rides_requested'] / ratio['active_drivers']
    return ratio

conn = sqlite3.connect('move.db')
rides = pd.read_sql_query("SELECT * FROM rides", conn)
drivers = pd.read_sql_query("SELECT * FROM drivers", conn)
conn.close()

rides['request_time'] = pd.to_datetime(rides['request_time'])
rides['hour'] = rides['request_time'].dt.hour

ds_hr = calc_demand_supply_ratio(rides, drivers, 'hour')
peak_hr = ds_hr.loc[ds_hr['rides_requested'].idxmax()]['hour']
highest_ds = ds_hr.loc[ds_hr['ds_ratio'].idxmax()]

zone_ds = calc_demand_supply_ratio(rides, drivers, 'zone')
highest_zone_ds = zone_ds.loc[zone_ds['ds_ratio'].idxmax()]

high_surge_hr = rides.groupby('hour')['surge_multiplier'].mean().idxmax()

print(f"Peak Demand Hour: {peak_hr}")
print(f"Highest DS Ratio Hour: {highest_ds['hour']}, Ratio: {highest_ds['ds_ratio']}")
print(f"Highest DS Ratio Zone: {highest_zone_ds['zone']}, Ratio: {highest_zone_ds['ds_ratio']}")
print(f"Highest Surge Hour: {high_surge_hr}")

# Regression
rides_with_ratio = pd.merge(rides, ds_hr[['hour', 'ds_ratio']], on='hour', how='left')
reg_data = rides_with_ratio.dropna(subset=['wait_time', 'ds_ratio'])

if len(reg_data) > 0:
    X = reg_data['ds_ratio']
    y = reg_data['wait_time']
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    print(f"R-squared: {model.rsquared}")
    print(f"Coefficient: {model.params['ds_ratio']}")
