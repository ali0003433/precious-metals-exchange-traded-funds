import pandas as pd
import numpy as np
from scipy import stats
import math
from sklearn.utils import resample
import matplotlib.pyplot as plt

def compare_pval_alpha(p_val, alpha):
    status = ''
    if p_val > alpha:
        status = "Fail to reject"
    else:
        status = 'Reject'
    return status


def bootstrap_sim(df, target_var, target_symbol, volability_period, n_sim = 1000):
    """
    This function gets the clean dataframe and compute the daily % 
    change. Then, it does resampling and geneate n_sim from daily % 
    change.  

    :param df: the input clean data frame
    :param target_var: variable including (close, open, high, low)
    :target_symbol including 'SLV', 'SIL', 'GLD', 'GDX', 'DJI'
    :n_sim it is the number of simulation
    :return 

    """
    #volability_period = 'M'
    df = df.loc[df['symbol'] == target_symbol]
    if df.index.name != 'date':
        df.set_index('date', inplace = True)
    #To compute daily % change and drop the first value
    daily_change = df[target_var].pct_change()
    daily_change.dropna(inplace=True)
    
    #To build an empty dataframe
    df_sim = pd.DataFrame()
    length = len(daily_change)
    count=0
    
    for i in range(n_sim):
        #sample same size as dataset, drop timestamp

        daily_change_sampling= resample(daily_change, replace=True, n_samples=length).reset_index(drop=True)
        
        
        #Add timestamp to shuffled data
        daily_change_sampling.index = df.index[1:]
        
        
        #Use standard deviation as a measure of volatility 
        # and multiplying by sqrt of number of months (12) or the number of season
        if volability_period == 'M':
            num_s = 12
        elif volability_period == 'Q':
            num_s = 4
        else:
            raise ValueError(f'The volability_period of {volability_period} is not valid')  
        monthly_vol_sampling = daily_change_sampling.resample(volability_period).std()* np.sqrt(num_s)
        
        
        #Rank the data on ascending order
        
        ranked_months_sampling = pd.DataFrame(monthly_vol_sampling.groupby(monthly_vol_sampling.index.year).rank()).reset_index()
        
        ranked_months_sampling.columns = ['period', 'ranking']
        
        #ranked_months_sampling['period'] = ranked_months_sampling['period'].map(lambda x: x.strftime('%b'))
        if volability_period == 'M':
            ranked_months_sampling['period'] = ranked_months_sampling['period'].map(lambda x: x.strftime('%b'))
        elif volability_period == 'Q':
            ranked_months_sampling['period'] = ranked_months_sampling['period'].dt.quarter.map(lambda x: 'Quarter ' + str(x))
        else:
            raise ValueError(f'The volability_period of {volability_period} is not valid') 
        
        sim_ranking = ranked_months_sampling.groupby('period').mean()
        
        #add each of 1000 sims into df
        df_sim = pd.concat([df_sim,sim_ranking],axis=1)
    all_ranking = df_sim.values.flatten()
    

    return df_sim, all_ranking

def hypothesis_test_one(alpha, VOL_ranking_df, df_clean, target_var, target_symbol,
                        volability_period, n_bootstrap = 1000, plot_option = False, season_for_plot ='Nov'):
    """
    Over the past 13 years, October has been the most volatile month 
    on average for the GLD stock and December the least volatile. The question
    is whether this is a persistent signal or just noise in the data?
    
    The goal of this function, here, is to statiscally analyze and test
    this phenomena to check whether is statistically significant or not.
    
    H0 : mu(for each month) = xbar the observed phenomena is not due chance
    HA : mu(for each month) not(=) xbar the observed phenomena is due chance
    
    :param alpha: the critical value of choice
    :param cleaned_data: the cleaned data including GLD prices used used 
    for hypothesis testing
    :return Pvalue,  This function return 
    """
    # Get data for tests
    df_sim, all_ranking = bootstrap_sim(df_clean, target_var, target_symbol,volability_period, n_bootstrap)
    VOL_ranking_mean = VOL_ranking_df.groupby('period').mean().reset_index()
    mean_ranking = all_ranking.mean()
    VOL_ranking_mean['pvalue'] = 2*VOL_ranking_mean['ranking'].\
    map(lambda x: np.sum(all_ranking > x) / all_ranking.shape[0]\
        if x > mean_ranking else np.sum(all_ranking < x) / all_ranking.shape[0])
    
    for month, p_val in zip(VOL_ranking_mean['period'], VOL_ranking_mean['pvalue']):
        # starter code for return statement and printed results
        status = compare_pval_alpha(p_val, alpha)
        assertion = ''
        if status == 'Fail to reject':
            assertion = 'cannot'
        else:
            assertion = "can"
        print(f'Based on the p value of {round(p_val,2)} and our alpha of {alpha} we {status.lower()}  the null hypothesis.'
              f'\n Due to these results, we  {assertion} state that the change in the volatility is due to chance in {month}')
        print('-'*100)
    if plot_option:
        fig, ax = plt.subplots(1,1,figsize = (8, 5));
        n, bins, patches = plt.hist(all_ranking, bins = 30, color = 'b', density = True);
        ax.set_ylabel('Probability density', fontsize=20);
        ax.set_xlabel('Average Ranking', fontsize=20);
        ax.set_title('Bootstrapping results', fontsize=20);
        upper_bound = float(VOL_ranking_mean.loc[VOL_ranking_mean['period'] == season_for_plot]['ranking'])
        lower_bound = mean_ranking - (upper_bound - mean_ranking)
        upper_bound = bins[(np.abs(bins - upper_bound)).argmin()]
        lower_bound = bins[(np.abs(bins - lower_bound)).argmin()]
        ax.axvline(upper_bound,color='r',ls='--', label='Dec Result',lw=3)
        ax.axvline(lower_bound,color='r',ls='--', label='Dec Result',lw=3)
        for c, p in zip(bins, patches):
            if c < lower_bound or c >= upper_bound:
                plt.setp(p, 'facecolor', 'r')
        pvalue = float(VOL_ranking_mean.loc[VOL_ranking_mean['period'] == season_for_plot]['pvalue'])
        ax.text(bins.max() - 0.23*(bins.max()-bins.min()), 0.3, f'P-value = {round(pvalue, 2)}', fontsize=16)
        plt.savefig(f'img/bootstraping_{target_symbol}_{target_var}_{season_for_plot}.png', transparent = False, figure = fig)
    return VOL_ranking_mean


def hypothesis_test_three_prep(df_clean, type=None, alpha=0.05):
    '''Prepares dataset for paired t-test.
       Signature: hypothesis_test_three_prep(df, type= None, alpha=0.05).
       type options: day, week, month'''

    df_clean['daily_movement'] = (df_clean.close-df_clean.open)*100/df_clean.open
    df_clean = df_clean.loc[df_clean['date'] >= '2014-10-06']
    df_clean_SLV = df_clean.loc[df_clean['symbol'] == 'SLV'][[
        'date', 'symbol', 'open', 'close', 'daily_movement']]
    df_clean_GLD = df_clean.loc[df_clean['symbol'] == 'GLD'][[
        'date', 'symbol', 'open', 'close', 'daily_movement']]

    if type == 'day':
        df_slv_vs_gld = pd.merge(df_clean_SLV,
                                 df_clean_GLD,
                                 how='left',
                                 on='date',
                                 suffixes=('_SLV', '_GLD'))
        df_slv_vs_gld['delta'] = df_slv_vs_gld['daily_movement_SLV'] - \
            df_slv_vs_gld['daily_movement_GLD']

    # Remove outliers
        data = df_slv_vs_gld[(np.abs(stats.zscore(
            df_slv_vs_gld[['daily_movement_SLV', 'daily_movement_GLD', 'delta']])) < 3).all(axis=1)]

        a = df_slv_vs_gld['daily_movement_SLV']
        b = df_slv_vs_gld['daily_movement_GLD']

    elif type == 'week':
        gld_weekly = df_clean_GLD.groupby(['symbol', pd.Grouper(key='date', freq='W')]).mean(
        ).reset_index().sort_values('date', ascending=False)[['date', 'open', 'close']]
        slv_weekly = df_clean_SLV.groupby(['symbol', pd.Grouper(key='date', freq='W')]).mean(
        ).reset_index().sort_values('date', ascending=False)[['date', 'open', 'close']]

        gld_weekly['wk_movement'] = (gld_weekly.open-gld_weekly.close)*100/gld_weekly.open
        slv_weekly['wk_movement'] = (slv_weekly.open-slv_weekly.close)*100/slv_weekly.open

        df_slv_vs_gld_wk = pd.merge(slv_weekly,
                                    gld_weekly,
                                    how='left',
                                    on='date',
                                    suffixes=('_SLV', '_GLD'))

        # Remove outliers
        df_slv_vs_gld_wk = df_slv_vs_gld_wk[(
            np.abs(stats.zscore(df_slv_vs_gld_wk[['wk_movement_SLV', 'wk_movement_GLD']])) < 3).all(axis=1)]

        a = df_slv_vs_gld_wk['wk_movement_SLV']
        b = df_slv_vs_gld_wk['wk_movement_GLD']

    elif type == 'month':

        gld_monthly = df_clean_GLD.groupby(['symbol', pd.Grouper(key='date', freq='M')]).mean(
        ).reset_index().sort_values('date', ascending=False)[['date', 'open', 'close']]
        slv_monthly = df_clean_SLV.groupby(['symbol', pd.Grouper(key='date', freq='M')]).mean(
        ).reset_index().sort_values('date', ascending=False)[['date', 'open', 'close']]

        gld_monthly['mo_movement'] = (gld_monthly.open-gld_monthly.close)*100/gld_monthly.open
        slv_monthly['mo_movement'] = (slv_monthly.open-slv_monthly.close)*100/slv_monthly.open

        df_slv_vs_gld_mo = pd.merge(slv_monthly,
                                    gld_monthly,
                                    how='left',
                                    on='date',
                                    suffixes=('_SLV', '_GLD'))

        # Remove outliers
        df_slv_vs_gld_mo = df_slv_vs_gld_mo[(
            np.abs(stats.zscore(df_slv_vs_gld_mo[['mo_movement_SLV', 'mo_movement_GLD']])) < 3).all(axis=1)]

        a = df_slv_vs_gld_mo['mo_movement_SLV']
        b = df_slv_vs_gld_mo['mo_movement_GLD']

    return a, b


def hypothesis_test_three_pttest(a, b, alpha=0.05):
    ''' Perform paired ttest.
        Parameters:
        a,b = array_like. The arrays must have the same shape.'''

    t_val, p_val = stats.ttest_rel(a, b)
    print(f"t_val = {t_val}, p_val = {p_val}")

    status = compare_pval_alpha(p_val, alpha)
    assertion = ''
    if status == 'Fail to reject':
        assertion = 'cannot'
    else:
        assertion = "can"

    # calculations for effect size, power, etc here as well
    spooled_S = np.sqrt(((a.std()**2 + b.std()**2)/2))
    coh_d = (a.mean() - b.mean()) / spooled_S
    
    print(f'Based on the p value of {p_val} and our alpha of {alpha} we {status.lower()}  the null hypothesis.'
          f'\nDue to these results, we  {assertion} state that there is a difference between daily movement of SLV and GLD')

    if assertion == 'can':
        print(f"with an effect size, cohen's d, of {str(coh_d)}.")
    else:
        print(".")

    return status

