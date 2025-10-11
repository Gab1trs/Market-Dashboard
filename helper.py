import yfinance as yf
import pandas as pd
import numpy as np

def data_download(ticker, start_date, end_date=None, save_csv=True):
    price = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)["Adj Close"]
    df = pd.DataFrame(price)
    df.columns = [ticker]

    df = df.iloc[1:].copy()

    ratio = df[ticker] / df[ticker].shift(1)      
    ret = ratio - 1                            

    log_inc = np.where(ratio > 0, np.log(ratio), 0.0)

    df   = df.iloc[1:].copy()
    ret  = ret.iloc[1:]
    log_inc = pd.Series(log_inc, index=ratio.index).iloc[1:]

    base = df[ticker].iloc[0]
    df["linear"]    = ret.cumsum() * 100          
    df["log_price"] = log_inc.cumsum() * 100      
    df["base100"]   = (df[ticker] / base) * 100   

    df.index.name = "Date"
    if save_csv:
        df.to_csv(f"{ticker}_data.csv")
    return df


def select_column_by_mode(df: pd.DataFrame, mode: str) -> pd.Series: 
    if mode =="Linear":
        return df["linear"]
    elif mode =="Logarithmic":
        return df["log_price"]
    elif mode =="Base 100":
        return df["base100"]
    elif mode =="Asset price":
        return df.iloc[:, 0]
    

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

# Check for missing values (do not work anymore as we have a dtaframe and not a series)
# def check_na(data):
    # null_sum=data.isna().sum()
    # null_percentage=null_sum/len(data)*100
    # print (f'Ratio of missing values: {null_percentage:.2f}%')

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

