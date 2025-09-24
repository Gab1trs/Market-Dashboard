import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

data=pd.read_csv('all_assets.csv', index_col=0, parse_dates=True)
data=data.ffill().dropna()
returns=data.pct_change()
cum_returns=(1+returns).cumprod()
assets=cum_returns.columns

with st.sidebar:
    selected_assets=st.multiselect("Select Assets", assets)
    min_date, max_date=st.date_input("Select Date Range", [data.index.min(), data.index.max()])

fig1=plt.figure(figsize=(10,6))
plt.plot(cum_returns.index, label=cum_returns.columns)
plt.legend()
plt.xlabel("Date")
plt.ylabel("Cumulative Returns")
plt.title("Cumulative Returns of All Assets")



