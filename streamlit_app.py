import streamlit as st
import pandas as pd

title = "Cross Asset REgime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)
# data=pd.read_csv('all_assets.csv', index_col=0, parse_dates=True)
# data=data.ffill().dropna()
# returns=data.pct_change()
# cum_returns=(1+returns).cumprod()

# st.dataframe(cum_returns)