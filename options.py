import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
import pandas_datareader.data as web
import math

# #function to compute the price of the call
# def black_scholes_call(S, K, T, r, sigma):

#     #standard black-scholes formula
#     d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
#     d2 = d1 - sigma * np.sqrt(T)

#     call = S * norm.cdf(d1) -  norm.cdf(d2)* K * np.exp(-r * T)
#     return call

# #function to compute the vega
# def vega(S, K, T, r, sigma):

#     d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    
#     vega = S  * np.sqrt(T) * norm.pdf(d1)
#     return vega

# #function to compute the implied volatilty from the option price
# def implied_volatility_call(C, S, K, T, r, tol=0.0001, max_iterations=1000):

#     #assigning initial volatility estimate for input in Newton-Raphson procedure
#     #this website helped me a lot to do the following : https://www.codearmo.com/blog/implied-volatility-european-call-python
#     sigma = np.sqrt((2*np.pi)/T)*(C/S)

#     for i in range(max_iterations):

#         #calculate difference between blackscholes price and market price with iteratively updated volality estimate
#         diff = black_scholes_call(S, K, T, r, sigma) - C

#         #break if difference is less than specified tolerance level
#         if abs(diff) < tol:
#             print(f'found on {i}th iteration')
#             print(f'difference is equal to {diff}')
#             break

#         #use Newton-Rapshon to update the estimate
#         sigma = sigma - diff / vega(S, K, T, r, sigma)
    
#     print(C)
#     print(S)
#     print(K)
#     print(T)
#     print(r)
#     print(f'cest le sigma : {sigma}')

#     return sigma

def bsm_option_price(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)


def calculate_implied_volatility(C, S, K, T, r):
    epsilon = 1e-6
    sigma = 0.5  # Initial guess for volatility
    max_iterations = 100
    iterations = 0

    # Lists to store iteration results for plotting
    iteration_values = []
    iv_values = []

    while True:
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T)
        option_price_estimate = bsm_option_price(S, K, T, r, sigma)

        iteration_values.append(iterations)
        iv_values.append(sigma)

        error = C - option_price_estimate
        if abs(error) < epsilon or iterations >= max_iterations:
            break

        sigma += error / vega
        iterations += 1

    return sigma #, iteration_values, iv_values


#we dynamically get the most recent interest rate of the 10Y T-Bond
end = dt.datetime.today()
start = (end - dt.timedelta(days=5)).strftime("%Y-%m-%d")
end = end.strftime("%Y-%m-%d")
interest_rate=web.DataReader('DGS10', 'fred', start, end).iloc[-1]
interest_rate = interest_rate.iloc[0]

#function to get the options chain
def get_options_chain(option_ticker: str) -> pd.DataFrame:

    all_options=[]
    chains = pd.DataFrame

    asset=yf.Ticker(option_ticker)
    expiration_dates=asset.options

    spot = asset.history(period="5d")["Close"].iloc[-1]

    for exp_date in expiration_dates:
        opt=asset.option_chain(exp_date)
        calls=opt.calls

        if calls.empty:
            continue
        
        #we take the expiration as the end of th day so that we don't have expired options
        calls['expiration'] = pd.to_datetime(exp_date) + pd.DateOffset(hours=23, minutes=59, seconds=59)
        calls["TimeToExpiration"] = ((calls["expiration"] - dt.datetime.today()).dt.days + 1)/365
        
        #this part adds to the list only the ATM option for each maturity
        closest_option_index=(calls['strike']-spot).abs().argmin()
        closest_option=calls.iloc[closest_option_index]
        all_options.append(closest_option)

    #we put our list in a new dataframe and compute the mid price which we use to compute implied volatility
    chains = pd.DataFrame(all_options)
    chains = chains.set_index('expiration')
    chains['mid']=(chains['ask']+chains['bid'])/2

    #we can now compute the implied volatility for each maturity
    chains['implied_volatility'] = chains.apply(lambda row : calculate_implied_volatility(C=row['mid'], S=spot, K=row['strike'], T=row['TimeToExpiration'], r=interest_rate), axis=1)

    trimmed_chains=chains[['strike', 'bid', 'ask','mid', 'TimeToExpiration', 'implied_volatility']].iloc[1:]

    return trimmed_chains
