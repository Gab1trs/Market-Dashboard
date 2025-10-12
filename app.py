import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from Market_Dashboard import startdate

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)
st.write(f"**To ease the use and efficiency of the Monitor, all the returns are calculated from {startdate}.**")

mode_to_file = {
    "Asset price": "all_assets_prices.csv",
    "Linear returns": "all_assets_linear.csv",
    "Logarithmic returns": "all_assets_log.csv",
    "Base 100 returns": "all_assets_base100.csv"
}

default_mode = "Asset price"
data = pd.read_csv(mode_to_file[default_mode], index_col=0, parse_dates=True)
assets = data.columns

with st.sidebar:
    selected_assets = st.multiselect("Select Assets", assets,  default=["SPY"])
    selected_mode = st.selectbox("Select Mode", list(mode_to_file.keys()))
    selected_timeframe = st.selectbox("Select Timeframe", ["3m", "6m", "YTD", "1Y", "5Y", "Max", "Custom"])
    if selected_timeframe != "Custom":
        if selected_timeframe == "3m":
            min_date = data.index.max() - pd.DateOffset(months=3)
        elif selected_timeframe == "6m":
            min_date = data.index.max() - pd.DateOffset(months=6)
        elif selected_timeframe == "YTD":
            min_date = pd.Timestamp(year=data.index.max().year, month=1, day=1)
        elif selected_timeframe == "1Y":
            min_date = data.index.max() - pd.DateOffset(years=1)
        elif selected_timeframe == "5Y":
            min_date = data.index.max() - pd.DateOffset(years=5)
        elif selected_timeframe == "Max":
            min_date = data.index.min()
        max_date = data.index.max()
    else:
        min_date, max_date = st.date_input("Select Date Range", [data.index.min(), data.index.max()])

data = pd.read_csv(mode_to_file[selected_mode], index_col=0, parse_dates=True)

# Filtre les données
filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()

if not filtered_data.empty:
    plt.style.use("seaborn-v0_8-darkgrid")
    fig1 = plt.figure(figsize=(12,7))
    plt.plot(filtered_data, linewidth=2)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel(selected_mode, fontsize=14)
    plt.title(f"{selected_mode} of Selected Assets", fontsize=16, fontweight="bold")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(selected_assets, fontsize=12, loc='upper left')
    fig1.autofmt_xdate()
    plt.tight_layout()
    st.pyplot(fig1)

else:
    st.write("Please select at least one asset to display the chart.")

