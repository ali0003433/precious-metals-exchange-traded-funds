import pandas as pd

def rename_columns(df):
    """
    This function is used to rename columns.
    """
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'symbol']
    return df

def change_format(df):
    """
    This function changes the format of the data
    """
    df['date'] = pd.to_datetime(df['date'])
    to_be_numeric = ['open', 'high', 'low', 'close', 'volume'] 
    df[to_be_numeric] = df[to_be_numeric].apply(pd.to_numeric) 
    return df

def clean_SLV(df, scale=10):
    """
    This function adjust the values for SLV.
    """
    numeric_cols = ['open', 'high', 'low', 'close', 'volume'] 
    df_sliced = df.loc[(df['symbol'] == 'SLV') & (df['date'] <= '2008-07-23'), numeric_cols]
    df.loc[(df['symbol'] == 'SLV') & (df['date'] <= '2008-07-23'), numeric_cols] = df_sliced / scale
    return df

def full_clean():
    """
    This function is implemented to clean the data.
    """
    #To read the data
    dirty_data = pd.read_csv('data/dirty_data.csv')
    cleaning_data1 = rename_columns(dirty_data)
    cleaning_data2 = change_format(cleaning_data1)
    cleaning_data3 = clean_SLV(cleaning_data2)
    
    cleaning_data3.to_csv('data/clean_data.csv')

    return cleaning_data3
