# Dashboard with equity (SPY), forex (USD), commodities (Gold, crude oil, wheat), bonds (Inflation-linked bonds).
# Data about growth, inflation, volatility, and yield.
# Data goes back as far as possible, with widget slider to choose time frame.


import datetime as dt
from helper import *

startdate="2000-01-01"
enddate=dt.datetime.today().strftime("%Y-%m-%d")


tickers = {
    "SPY": "SPY",
    "USD": "DX-Y.NYB",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",    
    "Wheat": "ZW=F",
    "Bond": "^TNX",
    "Inflation Bond": "TIP",
    "VIX": "^VIX",
}


dfs = {name: data_download(tkr, startdate, enddate) for name, tkr in tickers.items()}
dfs = {k: fill_missing_values(v) for k, v in dfs.items()}


# Concatenate all Series into one DataFrame
all_linear= pd.concat({k: v["linear"] for k, v in dfs.items()}, axis=1).dropna()
all_log= pd.concat({k: v["log_price"] for k, v in dfs.items()}, axis=1).dropna()
all_base= pd.concat({k: v["base100"] for k, v in dfs.items()}, axis=1).dropna()
all_prices= pd.concat({k: v[tickers[k]] for k, v in dfs.items()}, axis=1).dropna()

# Save to CSV
all_linear.to_csv("all_assets_linear.csv")
all_log.to_csv("all_assets_log.csv")
all_base.to_csv("all_assets_base100.csv")
all_prices.to_csv("all_assets_prices.csv")

# # Plot the data for each asset class
# assets_df.plot(figsize=(12, 7))
# plt.title("Cumulative Returns of Asset Classes")
# plt.xlabel("Date")
# plt.ylabel("Cumulative Return")
# plt.legend(loc='upper left')
# plt.show()


# fig, ax1=plt.subplots(figsize=(10,6))
# ax2=ax1.twinx()
# plt.title("SPY Closing Price Over Time")
# plt.yscale('log')

# # forex using USD index
# usd = (yf.download("DX-Y.NYB", start=spy.index.min())['Close'].pct_change() + 1).cumprod()
# common_index = spy.index.intersection(usd.index)
# ax1.plot(common_index, spy.loc[common_index], label='SPY', color='blue')
# ax2.plot(common_index, usd.loc[common_index], label='USD', color='red')

# lines_1, labels_1 = ax1.get_legend_handles_labels()
# lines_2, labels_2 = ax2.get_legend_handles_labels()
# ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
# plt.show()
