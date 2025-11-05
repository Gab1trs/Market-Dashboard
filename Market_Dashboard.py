import datetime as dt
from helper import *
from options import *
import pandas_datareader.data as web

startdate="1995-01-03"
enddate=dt.datetime.today().strftime("%Y-%m-%d")

#yahoo tickers for the chosen assets
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

#yahoo futures base symbols and suffixes
base_symbols={
    "SPY":"ES",
    "Gold":"GC",
    "Crude Oil":"CL",
    "Wheat":"ZW",
    "USD":"DX",
    "10Y T-Bond":"ZN"
}

suffixes={
    "SPY":".CME",
    "Gold":".CMX",
    "Crude Oil":".NYM",
    "Wheat":".CBT",
    "USD":".NYB",
    "10Y T-Bond":".CBT"
}

#yahoo option tickers for the chosen assets
option_tickers = {
    "SPY": "SPY",
    "USD": "UUP",
    "Gold": "GLD",
    "Crude Oil": "USO",
    "Wheat": "WEAT",
    "Inflation Bond": "TIP",
    "VIX": "VXX"
}


yields = {
"GDP": "GDP",
"DGS1MO": "US 1M",
"DGS3MO": "US 3M",
"DGS6MO": "US 6M",
"DGS1": "US 1Y",
"DGS2": "US 2Y",
"DGS3": "US 3Y",
"DGS5": "US 5Y",
"DGS7": "US 7Y",
"DGS10": "US 10Y",
"DGS20": "US 20Y",
"DGS30": "US 30Y",
"IRLTLT01DEM156N": "Germany 10Y",
"IRLTLT01FRM156N": "France 10Y",
"IRLTLT01ITM156N": "Italy 10Y",
"IRLTLT01GBM156N": "United Kingdom 10Y",
"IRLTLT01JPM156N": "Japan 10Y",
"IRLTLT01ESM156N": "Spain 10Y",
"IRLTLT01PTM156N": "Portugal 10Y",
"IRLTLT01GRM156N": "Greece 10Y",
}


#asset prices download and missing value filling
dfs = {name: data_download(tkr, startdate, enddate) for name, tkr in tickers.items()}
dfs = {k: fill_missing_values(v) for k, v in dfs.items()}

#we use different months for different futures contracts
futures_month_codes = {
    "Wheat": ['H', 'N', 'U', 'Z'],
    "Gold": ['F', 'G', 'J', 'K', 'M', 'Q', 'X', 'Z'],
    "Crude Oil": ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
}
default_future_months = ['H', 'M', 'U', 'Z']

futures = {name: download_futures_data(base,suffixes[name],futures_month_codes.get(name, default_future_months)) for name, base in base_symbols.items() if name in suffixes}

#we concatenate all prices into a single DataFrame and save individual futures dataframes
all_prices= pd.concat({k: v[tickers[k]] for k, v in dfs.items()}, axis=1).dropna()
for name, df in futures.items():
    df.to_csv(f"futures/{name.replace(' ', '_')}_futures.csv")

all_futures_prices = pd.concat({k: v['price'] for k, v in futures.items()}, axis=1).sort_index()

#align futures data with SPY expiration dates
if 'SPY' in futures and not futures['SPY'].empty:
    last_spy_expiration = futures['SPY'].index.max()
    all_futures_prices = all_futures_prices[all_futures_prices.index <= last_spy_expiration]

#normalize prices to starting value
all_futures_prices = (all_futures_prices / all_futures_prices.bfill().iloc[0])-1

#we get the option chains and create each CSV file
options = {name: get_options_chain(ticker) for name, ticker in option_tickers.items()}
for name, df in options.items():
    df.to_csv(f"options/{name.replace(' ', '_')}_options.csv")

all_option_chains=pd.concat({k: v['implied_volatility'] for k, v in options.items()}, axis=1).sort_index()

all_prices.to_csv("data/all_assets_prices.csv")
all_futures_prices.to_csv("futures/all_futures_prices.csv")
all_option_chains.to_csv("options/all_option_chains.csv")

#we download the CPI and yields data from the FRED database
cpi_data = web.DataReader('CPIAUCSL', 'fred', startdate, enddate)
cpi_data.to_csv("yields/cpi_data.csv")

yields_data = web.DataReader(list(yields.keys()), 'fred', startdate, enddate)
yields_data = yields_data.rename(columns=yields)
for ticker in yields_data.columns:
    filename = f"yields/{ticker.replace(' ', '_')}_yield.csv"
    yields_data[[ticker]].to_csv(filename)

all_yields = yields_data.sort_index().ffill()
all_yields.to_csv("yields/all_yields.csv")