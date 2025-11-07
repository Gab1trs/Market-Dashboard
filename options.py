import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np
from scipy.stats import norm
import pandas_datareader.data as web
import math

#function to compute the price of the call
def black_scholes_call(S, K, T, r, sigma):

    #standard black-scholes formula
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call = S * norm.cdf(d1) -  norm.cdf(d2)* K * np.exp(-r * T)
    return call

#function to compute the vega
def vega(S, K, T, r, sigma):

    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    
    vega = S  * np.sqrt(T) * norm.pdf(d1)
    return vega

#function to compute the implied volatilty from the option price
def implied_volatility_call(C, S, K, T, r, tol=0.0001, max_iterations=1000):

    #assigning initial volatility estimate for input in Newton-Raphson procedure
    #this website helped me a lot to do the following : https://www.codearmo.com/blog/implied-volatility-european-call-python
    sigma = np.sqrt((2*np.pi)/T)*(C/S)

    for i in range(max_iterations):

        #calculate difference between blackscholes price and market price with iteratively updated volality estimate
        diff = black_scholes_call(S, K, T, r, sigma) - C

        #break if difference is less than specified tolerance level
        if abs(diff) < tol:
            break

        #use Newton-Rapshon to update the estimate
        sigma = sigma - diff / vega(S, K, T, r, sigma)

    return sigma

# def _black_scholes_vega(S, K, T, r, sigma):
#     """
#     Calcule le prix d'une option et son Vega selon le modèle Black-Scholes.
#     Ceci est une fonction interne, préfixée par _.
#     """
#     if sigma <= 0 or T <= 0:
#         return np.nan, np.nan

#     d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
#     d2 = d1 - sigma * math.sqrt(T)
    
#     price = (S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2))
#     vega = S * norm.pdf(d1) * math.sqrt(T)
    
#     return price, vega

# def implied_volatility(C, S, K, T, r, tol=1e-6, max_iter=100):
#     """
#     Calcule la volatilité implicite en utilisant la méthode de Newton-Raphson.

#     :param S: Prix spot de l'actif sous-jacent
#     :param K: Prix d'exercice (Strike)
#     :param T: Temps jusqu'à l'expiration (en années)
#     :param r: Taux d'intérêt sans risque
#     :param market_price: Prix de l'option observé sur le marché
#     :param tol: Tolérance pour la convergence
#     :param max_iter: Nombre maximum d'itérations
#     :return: Volatilité implicite (ou np.nan si non trouvée)
#     """
#     # Vérification de rationalité (valeur intrinsèque)
#     intrinsic_value = max(0, S - K)
#     if C < intrinsic_value * 0.99: # On laisse une petite marge
#         return np.nan

#     sigma = 0.5  # Estimation initiale de la volatilité

#     for i in range(max_iter):
#         price, vega = _black_scholes_vega(S, K, T, r, sigma)

#         if np.isnan(price) or np.isnan(vega):
#             return np.nan

#         # Garde-fou : si vega est trop petit, la méthode diverge
#         if vega < 1e-8:
#             return np.nan

#         error = price - C

#         # Si l'erreur est suffisamment petite, on a trouvé la solution
#         if abs(error) < tol:
#             return sigma

#         # Mise à jour de sigma selon Newton-Raphson
#         sigma -= error / vega
        
#         # Garde-fou : on garde sigma dans des bornes raisonnables
#         sigma = max(1e-4, min(sigma, 5.0))

#     return np.nan # Retourne NaN si la convergence n'est pas atteinte


#we dynamically get the most recent interest rate of the 10Y T-Bond
end = dt.datetime.today()
start = (end - dt.timedelta(days=5)).strftime("%Y-%m-%d")
end = end.strftime("%Y-%m-%d")
interest_rate=web.DataReader('DGS10', 'fred', start, end).iloc[-1]
interest_rate = (interest_rate.iloc[0])/100

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
    chains['implied_volatility'] = chains.apply(lambda row : implied_volatility_call(C=row['mid'], S=spot, K=row['strike'], T=row['TimeToExpiration'], r=interest_rate), axis=1)

    trimmed_chains=chains[['strike', 'bid', 'ask','mid', 'TimeToExpiration', 'implied_volatility']].iloc[1:]

    return trimmed_chains
