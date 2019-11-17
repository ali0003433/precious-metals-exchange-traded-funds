''' This script compiles data from Alpha Vantage API
    and transforms the JSON output into a dataframe and CSV file'''
import requests
import pandas as pd
import json


def get_keys(path):
    '''get API key'''
    with open(path) as f:
        return json.load(f)['api_key']


def call_api_one_symbol(symbol, verbose=True):
    '''call API and compile data for each symbol'''
    api_key = get_keys("/Users/alyssaliguori/secret/alpha_vantage_key.json")
    URL = 'https://www.alphavantage.co/query?'
    PARAMS = {'function': 'TIME_SERIES_DAILY',
              'symbol': symbol,
              'outputsize': 'full',
              'apikey': api_key
              }
    response = requests.get(URL, PARAMS)
    if response.status_code == 200:
        if verbose:
            print(f'The response code for {symbol} is {response.status_code}')
    else:
        raise ValueError(
            f'Error getting data from {url} API. Response code: {response.status_code}')
    df = pd.DataFrame(response.json()['Time Series (Daily)']).T
    df['symbol'] = symbol
    df.columns = ['open', 'high', 'low', 'close', 'volume', 'symbol']
    df.to_csv(f'data/raw_{symbol}.csv')
    return df


def call_all_symbols(symbol_list):
    '''Calls the API for each symbol in symbol_list and returns
    pandas dataframe in long format, concatenating all dataframes'''
    for i, symbol in enumerate(symbol_list):
        if i == 0:
            df = call_api_one_symbol(symbol)
        else:
            df = pd.concat([df, call_api_one_symbol(symbol)])
    df.to_csv('data/dirty_data.csv')
    return df
