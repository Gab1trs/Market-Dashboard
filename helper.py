import yfinance as yf
import pandas as pd
import numpy as np

def data_download(ticker, start_date, end_date=None, save_csv=True):
    price = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)["Adj Close"]
    df = price.to_frame("price").sort_index()
    ret = df["price"].pct_change().fillna(0)
    df["linear"]     = (1 + ret).cumprod() * 100
    df["base100"]    = (df["price"] / df["price"].iloc[0]) * 100
    df["log_price"]  = np.log(1 + ret).cumsum() * 100  
    df.index.name = "Date"
    
    if save_csv:
        df.to_csv(f"{ticker}_data.csv", index=True)
    return df


def select_column_by_mode(df: pd.DataFrame, mode: str) -> pd.Series: 
    if mode =="Linear":
        return df["linear"]
    elif mode =="Logarithmic":
        return df["log_price"]
    elif mode =="Base 100":
        return df["base100"]
    

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

# Check for missing values
def check_na(data):
    null_sum=data.isna().sum()
    null_percentage=null_sum/len(data)*100
    print (f'Ratio of missing values: {null_percentage:.2f}%')

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

