import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

#names for the tickers ans their CSV files
ticker_filename={
    "SPY":"SPY_data.csv",
    "DX-Y.NYB":"USD_data.csv",
    "GC=F":"Gold_data.csv",
    "CL=F":"Crude_Oil_data.csv",
    "ZW=F":"Wheat_data.csv",
    "^TNX":"10Y-T-Bond_data.csv",
    "TIP":"Inflation_Bond_data.csv",  
    "^VIX":"VIX_data.csv"       
}
#function to donwload the prices from Yahoo Finance
def data_download(ticker, start_date, end_date=None, save_csv=True):
    price = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)["Adj Close"] 
    df = pd.DataFrame(price)
    df.columns = [ticker]   

    df.index.name = "Date"
    if save_csv:
        df.to_csv(f'data/{ticker_filename[ticker]}')
    return df

#function to compute linear cumulated returns    
def calc_linear(df):
    linear = df.pct_change().add(1).cumprod()
    linear.iloc[0] = 1
    return linear

#function to compute logarithmic cumulated returns    
def calc_log(df):
    ratio = df.pct_change() + 1
    log_cum = ratio.where(ratio > 0).apply(np.log).cumsum() #we apply it only when ratio > 0 to avoid errors
    linear = calc_linear(df)
    for col in log_cum.columns: #for loop to replace log returns by linear return when ratio < 0 to ensure returns consistency
        log_cum.iloc[0, log_cum.columns.get_loc(col)] = 0
        mask = ratio[col] <= 0
        log_cum.loc[mask, col] = linear.loc[mask, col]
    return log_cum

#function to compute volatility of the dataframe
def calc_vol(df, timeframe):
    vol_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        #we need to compute the vol for T-bonds differently because it's a yield, not a price. So we cannot use .std() directly
        if col == "10Y T-Bond":
            n_years = 10
            y_annual = df[col]/100
            y_semi = y_annual/2 #T-bonds are semi annual
            n_semi = n_years*2
            
            macaulay_duration_semi=(1+y_semi)/y_semi*(1-1/(1+y_semi)**n_semi)
            modified_duration_years = (macaulay_duration_semi/(1+y_semi))/2
            yield_change = df[col].diff()/100
            price_change = -modified_duration_years*yield_change #this is where we convert the yield into a price change
            vol_df[col] = price_change.rolling(window=timeframe).std()*np.sqrt(252)

        else:
            vol_df[col] = df[col].pct_change().rolling(window=timeframe).std() * np.sqrt(252)
            
    return vol_df

#function to compute T-bond returns using different methods. This will help us to display the right number when we choose a mode in streamlit sidebar
def calc_bond_price_returns(df_yield, mode='linear'):
    #the beginning of the function is the same than the one to compute volatility
    yield_series = df_yield.iloc[:, 0]
    n_years = 10
    y_annual = yield_series / 100
    y_semi = y_annual/2
    n_semi = n_years * 2
    
    macaulay_duration_semi = (1 + y_semi)/y_semi * (1 - 1 / (1 + y_semi)**n_semi)
    modified_duration_years = (macaulay_duration_semi / (1 + y_semi)) / 2
    yield_change = yield_series.diff()/100
    price_change = -modified_duration_years * yield_change

    if mode == 'linear':
        returns = (1+price_change).cumprod()
        returns.iloc[0]=1 
        return returns.to_frame(df_yield.columns[0])
    elif mode == 'log':
        log_returns = price_change.cumsum()
        log_returns.iloc[0]=0
        return log_returns.to_frame(df_yield.columns[0])
    elif mode == 'log_daily':
        price_change.iloc[0]=0
        return price_change.to_frame(df_yield.columns[0])

 #function to define the growth/recession regime based on the performance of the S&P. We use a window of 120 days to target longer macro regimes   
def proxy_global(df, window=120):
    spy_proxy = df['SPY'].pct_change().rolling(window=window).mean()
    persistent_signal=spy_proxy.rolling(window=10).mean() #we compare to a rolling mean of 10 days to avoid false signals
    conditions = [persistent_signal > 0]
    choices = ['Growth']

    df['regime'] = np.select(conditions, choices, default='Recession')
    return df

#simple function to clean the data
def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

#function to define the inflation growth/decline regimes based on the CPI data of the FRED
def calculate_realized_inflation_regime(price_data, cpi_data, window=6):
    inflation_yoy = cpi_data['CPIAUCSL'].pct_change(periods=12) * 100
    daily_inflation = inflation_yoy.reindex(price_data.index, method='ffill').dropna() #we transform the monthly format of CPI data into daily format
    inflation_trend = daily_inflation.rolling(window=window * 21).mean()
    persistent_inflation = inflation_trend.rolling(window=10).mean()
    conditions = [daily_inflation > persistent_inflation]
    choices = ['Inflation growth']
    return pd.Series(np.select(conditions, choices, default='Inflation decline'), index=daily_inflation.index)

#function to get the list of tickers we want to retrieve for the futures
def get_futures_chain(base_symbol: str, exchange_suffix: str, month_codes: list[str]) -> list[str]:

    today = dt.date.today()
    current_year = today.year
    
    futures_chain = []
    
    #on YF, all the futures tickers are different so we need to dynamically build the good format to retrieve the data
    for year in range(current_year, current_year + 2):
        year_code = str(year)[-2:]
        for month_code in month_codes:
            future_ticker = f"{base_symbol}{month_code}{year_code}{exchange_suffix}" 
            futures_chain.append(future_ticker)
            
    return futures_chain

#using the previous function, we can now retrieve the future prices using the list we created
def download_futures_data(base_symbol: str, exchange_suffix: str, month_codes: list[str]) -> pd.DataFrame:
    REVERSE_MONTH_CODES = {
        'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
        'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12
    }
    
    futures_chain = get_futures_chain(base_symbol, exchange_suffix, month_codes)
    price_data = []

    for ticker in futures_chain:
        try:
            history = yf.Ticker(ticker).history(period="5d") 
            if history.empty:
                continue
            #we get the last future price which is the only one we are interested in
            last_price = history['Close'].iloc[-1]

            #we strip our ticker to extract the expiration date, and we store the info of each future in a new dataframe
            main_part = ticker.split('.')[0]
            year_str = ''.join(filter(str.isdigit, main_part))
            month_code = ''.join(filter(str.isalpha, main_part))[-1]
            
            month = REVERSE_MONTH_CODES[month_code]
            year = 2000 + int(year_str)
            
            expiration_date = dt.date(year, month, 30)

            price_data.append({
                'expiration': expiration_date,
                'ticker': ticker,
                'price': last_price
            })

        except Exception:
            continue

    if not price_data:
        return pd.DataFrame(columns=['ticker', 'price'])

    df = pd.DataFrame(price_data)
    df = df.set_index('expiration')
    df.index.name = 'expiration'

    return df[['ticker', 'price']]

#function the get the correlation matrix of our assets
def calc_correlation(df):

    log_returns_df = pd.DataFrame(index=df.index)

    bond_cols = [col for col in df.columns if col == '10Y T-Bond']
    other_cols = [col for col in df.columns if col != '10Y T-Bond']

    #again, we need to make sure we do not compute returns for T-Bonds the same way we do for others as it is a yield
    if other_cols:
        calc_cols = df.select_dtypes(include=np.number).columns
        final_calc_cols = [col for col in calc_cols if col not in bond_cols]
        other_returns = np.log(df[final_calc_cols] / df[final_calc_cols].shift(1))
        log_returns_df = log_returns_df.join(other_returns)

    if bond_cols:
        bond_returns = calc_bond_price_returns(df[bond_cols], mode='log_daily')
        log_returns_df = log_returns_df.join(bond_returns)

    matrix = log_returns_df.corr()
    return matrix
