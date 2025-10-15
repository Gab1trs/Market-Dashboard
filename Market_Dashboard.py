import datetime as dt
from helper import *
import pandas_datareader.data as web

startdate="2003-12-08"
enddate=dt.datetime.today().strftime("%Y-%m-%d")


tickers = {
    "SPY": "SPY",
    "USD": "DX-Y.NYB",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",    
    "Wheat": "ZW=F",
    "10Y T-Bond": "^TNX",
    "Inflation Bond": "TIP",
    "VIX": "^VIX",
}


dfs = {name: data_download(tkr, startdate, enddate) for name, tkr in tickers.items()}
dfs = {k: fill_missing_values(v) for k, v in dfs.items()}


all_prices= pd.concat({k: v[tickers[k]] for k, v in dfs.items()}, axis=1).dropna()

all_prices.to_csv("data/all_assets_prices.csv")

cpi_data = web.DataReader('CPIAUCSL', 'fred', startdate, enddate)
cpi_data.to_csv("data/cpi_data.csv")



