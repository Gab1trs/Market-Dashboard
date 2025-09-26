import yfinance as yf
import pandas as pd

def data_download(ticker, start_date, end_date=None):
    data = yf.download(ticker, start=start_date, end=end_date)['Close']
    data.to_csv(f"{ticker}_data.csv")
    return (pd.read_csv(f"{ticker}_data.csv", index_col=0, parse_dates=True)[ticker].pct_change() + 1).cumprod() 

ticker_filename={
    "SPY":"spy_data.csv",
    "DX-Y.NYB":"usd_data.csv",
    "GC=F":"gold_data.csv",
    "WTI":"crude_oil_data.csv",
    "ZW=F":"wheat_data.csv",
    "^TNX":"bond_data.csv"
}

# Check for missing values
def check_na(data):
    null_sum=data.isna().sum()
    null_percentage=null_sum/len(data)*100
    print (f'Ratio of missing values: {null_percentage:.2f}%')

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

