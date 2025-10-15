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
    "TIP":"tips_data.csv",  #inflation linked US (this is an ETF)
    "^VIX":"vix_data.csv"       
}

def data_download(ticker, start_date, end_date=None, save_csv=True):
    price = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)["Adj Close"]
    df = pd.DataFrame(price)
    df.columns = [ticker]   

    df.index.name = "Date"
    if save_csv:
        df.to_csv(f'data/{ticker_filename[ticker]}')
    return df
    
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

def calc_vol(df, timeframe):
    vol_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        if col == "10Y T-Bond":
            n_years = 10
            y_annual = df[col]/100
            y_semi = y_annual/2
            n_semi = n_years*2
            
            macaulay_duration_semi=(1+y_semi)/y_semi*(1-1/(1+y_semi)**n_semi)
            modified_duration_years = (macaulay_duration_semi/(1+y_semi))/2
            yield_change = df[col].diff()/100
            price_change = -modified_duration_years*yield_change
            vol_df[col] = price_change.rolling(window=timeframe).std()*np.sqrt(252)

        else:
            vol_df[col] = df[col].pct_change().rolling(window=timeframe).std() * np.sqrt(252)
            
    return vol_df

def calc_bond_price_returns(df_yield, mode='linear'):
    yield_series = df_yield.iloc[:, 0]
    n_years = 10
    y_annual = yield_series / 100
    y_semi = y_annual/2
    n_semi = n_years/2
    
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
    
def proxy_global(df, window=63):
    spy_proxy = df['SPY'].pct_change().rolling(window=window).mean()
    spread = df['SPY'].pct_change() - df['10Y T-Bond'].diff()
    conditions = [
        (spy_proxy > 0) & (spread > 0), 
        (spy_proxy < 0) & (spread < 0)   
    ]
    choices = ['Growth', 'Recession']

    df['regime'] = np.select(conditions, choices, default='Neutral')
    return df

def fill_missing_values(df):
    df=df.ffill().dropna()
    return df

