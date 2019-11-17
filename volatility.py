import pandas as pd
import numpy as np
def compute_volatility(df, target_var, target_symbol, volability_period = 'M'):
    """
    This function compute the average volatility for each month
    
    :param df: input clean data frame
    :param target_var: variable including (close, open, high, low)
    :target_symbol including 'SLV', 'SIL', 'GLD', 'GDX', 'DJI'
    :return VOL_ranking_mean: a data frame including average of
    volatility ranking per month and standard deviation of volatility ranking per month
    :return monthly_vol: the value of volability per month for all years
    """
    df = df.loc[df['symbol'] == target_symbol]
    if df.index.name != 'date':
        df.set_index('date', inplace = True)
    #To compute daily % change and drop the first value
    daily_change = df[target_var].pct_change()
    daily_change.dropna(inplace=True)
    #Use standard deviation as a measure of volatility 
    # and multiplying by sqrt of number of months (12) or number of season
    if volability_period == 'M':
        num_s = 12
    elif volability_period == 'Q':
        num_s = 4
    else:
        raise ValueError(f'The volability_period of {volability_period} is not valid')  
    
    monthly_vol = daily_change.resample(volability_period).std()* np.sqrt(num_s)
    #Rank the data on ascending order
    ranked_months = pd.DataFrame(monthly_vol.groupby(monthly_vol.index.year).rank()).reset_index()
    ranked_months.columns = ['period', 'ranking']
    #To build a data frame
    monthly_vol_df = pd.DataFrame(monthly_vol).reset_index()
    monthly_vol_df.columns = ['period', 'volatility']
    if volability_period == 'M':
        ranked_months['period'] = ranked_months['period'].map(lambda x: x.strftime('%b'))
        monthly_vol_df['period'] = monthly_vol_df['period'].map(lambda x: x.strftime('%b'))
    elif volability_period == 'Q':
        ranked_months['period'] = ranked_months['period'].dt.quarter.map(lambda x: 'Quarter ' + str(x))
        monthly_vol_df['period'] = monthly_vol_df['period'].dt.quarter.map(lambda x: 'Quarter ' + str(x))
    else:
        raise ValueError(f'The volability_period of {volability_period} is not valid') 
        
    
    return (monthly_vol_df, ranked_months)