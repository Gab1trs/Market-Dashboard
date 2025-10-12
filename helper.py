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

    r = df[ticker].pct_change()
    ratio = r + 1

    df["linear"] = (r+1).cumprod()
    
    log_inc = np.where(ratio > 0, np.log(ratio), np.nan)
    log_cum = pd.Series(log_inc, index=df.index).cumsum()
    mask_invalid = ~(ratio > 0)
    log_price = log_cum.copy()
    log_price[mask_invalid] = df["linear"][mask_invalid]
    df["log_price"] = log_price
    df = df.dropna()     

    df.index.name = "Date"
    if save_csv:
        df.to_csv(ticker_filename[ticker])
    return df

def select_column_by_mode(df: pd.DataFrame, mode: str) -> pd.Series: 
    if mode =="Linear":
        return df["linear"]
    elif mode =="Logarithmic":
        return df["log_price"]
    elif mode =="Asset price":
        return df.iloc[:, 0]
    
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

# Check for missing values (do not work anymore as we have a dtaframe and not a series)
# def check_na(data):
    # null_sum=data.isna().sum()
    # null_percentage=null_sum/len(data)*100
    # print (f'Ratio of missing values: {null_percentage:.2f}%')

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

