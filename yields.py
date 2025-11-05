import pandas as pd

us_yields = [
"US 1M","US 3M","US 6M","US 1Y","US 2Y","US 3Y","US 5Y","US 7Y","US 10Y","US 20Y","US 30Y"
]

countries_10Y_yields = [
    "US 10Y",
    "Germany 10Y",
    "France 10Y",
    "Italy 10Y",
    "United Kingdom 10Y",
    "Japan 10Y",
    "Spain 10Y",
    "Portugal 10Y",
    "Greece 10Y"
]

#function to get the yield curve for the US
def get_yield_curve(df):

    latest_us_yield= df[us_yields].iloc[-1]
    latest_us_yield.index = latest_us_yield.index.str.split(' ').str[1]

    return latest_us_yield

#function to get the last 10Y yields of all the countries we listed above (by using the tickers in Market_Dashboard.py)
def get_countries_yields(df):

    latest_countries_yield= df[countries_10Y_yields].iloc[-1]
    latest_countries_yield.index = latest_countries_yield.index.str.split(' ').str[0]
    new_index = latest_countries_yield.index.tolist()
    new_index[4] = "UK"
    latest_countries_yield.index = new_index

    return latest_countries_yield