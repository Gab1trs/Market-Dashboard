# Dashboard with equity (SPY), forex (USD), commodities (Gold, crude oil, wheat), bonds (Inflation-linked bonds).
# Data about growth, inflation, volatility, and yield.
# Data goes back as far as possible, with widget slider to choose time frame.


import datetime as dt
from helper import *

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

# Concatenate all Series into one DataFrame

all_prices= pd.concat({k: v[tickers[k]] for k, v in dfs.items()}, axis=1).dropna()

all_prices.to_csv("data/all_assets_prices.csv")

