import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Set specific parameters for the visualizations
large = 22; med = 16; small = 12
params = {'axes.titlesize': large,
          'legend.fontsize': med,
          'figure.figsize': (16, 10),
          'axes.labelsize': med,
          'xtick.labelsize': med,
          'ytick.labelsize': med,
          'figure.titlesize': large}
plt.rcParams.update(params)
plt.style.use('seaborn-whitegrid')
sns.set_style("white")


def overlapping_density(package=None, input_vars=None, target_vars=None):
    """
    Set the characteristics of your overlapping density plot
    All arguments are set to None purely as a filler right now

    Function takes package name, input variables(categories), and target variable as input.
    Returns a figure

    Should be able to call this function in later visualization code.

    PARAMETERS

    :param package:        should only take sns or matplotlib as inputs, any other value should throw and error
    :param input_vars:     should take the x variables/categories you want to plot
    :param target_vars:    the y variable of your plot, what you are comparing
    :return:               fig to be enhanced in subsequent visualization functions
    """

    # Set size of figure
    fig = plt.figure(figsize=(16, 10), dpi=80)

    # Starter code for figuring out which package to use
    if package == "sns":
        for variable in input_vars:
            sns.kdeplot(...)
    elif package == 'matplotlib':
        for variable in input_vars:
            plt.plot(..., label=None, linewidth=None, color=None, figure = fig)

    return fig



def boxplot_plot(package=None, input_vars=None, target_vars=None):
    """
    Same specifications and requirements as overlapping density plot

    Function takes package name, input variables(categories), and target variable as input.
    Returns a figure

    PARAMETERS

    :param package:        should only take sns or matplotlib as inputs, any other value should throw and error
    :param input_vars:     should take the x variables/categories you want to plot
    :param target_vars:    the y variable of your plot, what you are comparing
    :return:               fig to be enhanced in subsequent visualization functions
    """
    plt.figure(figsize=(16, 10), dpi=80)

    pass
def visualizations_four(df, symbols, type_price = 'close',
                   start_date = '2000-01-01', end_date = '2010-01-01',
                   fill_na = 'ffill',  moving_average_plot = False , 
                   short_window = None , long_window = None):
    """
    This function get a dataframe as input
    and make several visualizations
    
    inputs are:
    df : data frame
    symbol: showing the previous metal
    start_date: the start date for ploting
    end_date: the end date for ploting
    short_window and long_window are used for making the moving averages plots
    fill_na: Method to use for filling holes in reindexed Series pad / ffill: propagate last valid observation forward to next     valid backfill / bfill: use next valid observation to fill gap.
    """
    df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if df.index.name != 'date':
        df.set_index('date', inplace = True)
        
     # Plot everything by leveraging the very powerful matplotlib package
    fig, ax = plt.subplots(figsize=(16,9))
  
    for symbol in symbols:
        #slic the data frame
        df_symbol = df.loc[df['symbol'] == symbol]
    
        # Getting just the adjusted prices. This will return a Pandas DataFrame
        # The index in this DataFrame is the major index of the panel_data.
        price = df_symbol[type_price] 

        # Getting all weekdays between start_date and end_date
        all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')

        #Align the existing prices in adj price with our new set of dates.
        # Reindex price using all_weekdays as the new index
        price = price.reindex(all_weekdays)

        # Reindexing will insert missing values (NaN) for the dates that were not present
        # in the original set. To cope with this, we can fill the missing by replacing them
        # with the latest available price for each instrument.
        price = price.fillna(method='ffill')

        ax.plot(price.index, price, label= f'{symbol}')
        if moving_average_plot:
            # Calculate the 20 and 100 days moving averages of the closing prices
            short_rolling = price.rolling(window=20).mean()
            long_rolling = price.rolling(window=100).mean()
            ax.plot(short_rolling.index, short_rolling, label=f'{short_window} days rolling')
            ax.plot(long_rolling.index, long_rolling, label=f'{long_window} days rolling')
    ax.set_xlabel('Date', fontsize = 16)
    ax.set_title('Closing price', fontsize = 18)
    ax.set_ylabel('Price ($)', fontsize = 16)
    ax.legend()
    plt.savefig(f'img/Time_series.png', transparent = False, figure = fig)

def visualization_one(volatility_set, target_symbol, target_var, output_image_name=None):
    """
    This function is used to visualize the average volatility for each month
    
    :param target_var: variable including (close, open, high, low)
    :target_symbol including 'SLV', 'SIL', 'GLD', 'GDX', 'DJI'
    :volatility_set: a set including volatility ranking and volatility values
    """
    sns.set(font_scale=3)
    #df_clean = pd.read_csv('data/clean_data.csv')

    monthly_vol_df, VOL_ranking_df = volatility_set
    my_order = VOL_ranking_df.groupby("period")["ranking"].mean().sort_values(ascending=False).index
    #my_order = monthly_vol_df.groupby("month")["volatility"].mean().sort_values(ascending=False).index

    fig, axes = plt.subplots(2,1, figsize = (20, 14))
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    #sns.set(style="white", context="talk")
    g = sns.violinplot(x= 'period', y = 'volatility', data = monthly_vol_df, order = my_order, ax= axes[0], color = 'skyblue');
    axes[0].set_xlabel('', fontsize=22)
    axes[0].set_ylabel('Volatility', fontsize=24);
    axes[0].set_title(f'Average Volatility for {target_symbol}', fontsize=26);
    axes[0].tick_params(labelsize=24)

    
    g1 = sns.barplot(x='period',y='ranking', data = VOL_ranking_df, ax = axes[1], order = my_order, color = 'palegreen')

    groupedvalues=VOL_ranking_df.groupby('period').mean().reset_index()
    for index, order in enumerate(my_order):
        row = groupedvalues.loc[groupedvalues['period'] == order]
        axes[1].text(index-0.2,float(row['ranking'])+0.05,
                     round(float(row['ranking']),2),
                     color='black', ha="center",
                    fontsize = 16)
    axes[1].set_xlabel('', fontsize=24);
    axes[1].set_ylabel('Ranking', fontsize=22);
    axes[1].set_title(f'Ranking based on volatility for {target_symbol}', fontsize=26);
    axes[1].tick_params(labelsize=24)
    #plt.legend()

    # exporting the image to the img folder
    plt.savefig(f'img/{output_image_name}.png', transparent = False, figure = fig)



def visualization_SLV_vs_GLD_5yrs(df_clean, date='2014-10-06'):
    """
    This function is used to visualize the long term movement of SLV and GLD
    Takes two arguments: clean data and the date when the 5-year period starts.
    
    """
    #Preparing the dataset
    df_clean_SLV = df_clean.loc[df_clean['symbol'] == 'SLV'][['date','symbol','open','close']]
    df_clean_GLD = df_clean.loc[df_clean['symbol'] == 'GLD'][['date','symbol','open','close']]
    df_clean_GLD.date.isin(df_clean_SLV.date).value_counts()
    
    SLV_scaled = df_clean_SLV.loc[df_clean_SLV.date>=date].copy()
    GLD_scaled = df_clean_GLD.loc[df_clean_GLD.date>=date].copy()

    SLV_scaled['scale'] = SLV_scaled['close']/SLV_scaled.iloc[-1]['close']
    GLD_scaled['scale'] = GLD_scaled['close']/GLD_scaled.iloc[-1]['close']

    SLV_scaled['pct_change'] = SLV_scaled.close.pct_change()*100
    GLD_scaled['pct_change'] = GLD_scaled.close.pct_change()*100
    SLV_scaled = SLV_scaled.fillna(value=0)
    GLD_scaled = GLD_scaled.fillna(value=0)

    #Plotting figure
    plt.figure(figsize = (10,6))
    plt.style.use('fivethirtyeight')
    plt.plot(SLV_scaled['date'], SLV_scaled['scale'],label='SLV Price',c='silver')
    plt.plot(GLD_scaled['date'], GLD_scaled['scale'],label='GLD Price',c='gold')
    plt.title("SLV ETF Price vs GLD ETF Price, Normalized to 2014/10/06")
    plt.ylabel('Price normalized to price at 2014/10/06')
    plt.legend()

    # exporting the image to the img folder
    plt.savefig('img/SLV_vs_GLD_5yrs')

    

def visualization_three(output_image_name):
    pass

def visualization_four(output_image_name):
    pass