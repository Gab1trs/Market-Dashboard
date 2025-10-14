import yfinance as yf
import pandas as pd
import numpy as np

ticker_filename={
    "SPY":"spy_data.csv",
    "DX-Y.NYB":"usd_data.csv",
    "GC=F":"gold_data.csv",
    "CL=F":"crude_oil_data.csv",
    "ZW=F":"wheat_data.csv",
    "^TNX":"bond_data.csv",
    "TIP":"tips_data.csv",  #inflaton linked US
    "^VIX":"vix_data.csv"       
}

def data_download(ticker, start_date, end_date=None, save_csv=True):
    price = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)["Adj Close"]
    df = pd.DataFrame(price)
    df.columns = [ticker]   

    df.index.name = "Date"
    if save_csv:
        df.to_csv(f'data/{ticker_filename[ticker]}')
    return df
    
def calc_linear(df):
    linear = df.pct_change().add(1).cumprod()
    linear.iloc[0] = 1
    return linear
    
def calc_log(df):
    ratio = df.pct_change() + 1
    log_cum = ratio.where(ratio > 0).apply(np.log).cumsum()
    linear = calc_linear(df)
    for col in log_cum.columns:
        log_cum.iloc[0, log_cum.columns.get_loc(col)] = 0
        mask = ratio[col] <= 0
        log_cum.loc[mask, col] = linear.loc[mask, col]
    return log_cum

# Check for missing values (do not work anymore as we have a dataframe and not a series)
# def check_na(data):
    # null_sum=data.isna().sum()
    # null_percentage=null_sum/len(data)*100
    # print (f'Ratio of missing values: {null_percentage:.2f}%')

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

