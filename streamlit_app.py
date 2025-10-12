import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

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
    selected_assets = st.multiselect("Select Assets", assets)
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
    fig1 = plt.figure(figsize=(10,6))
    plt.plot(filtered_data)
    plt.legend(selected_assets)
    plt.xlabel("Date")
    plt.ylabel(selected_mode)
    plt.title(f"{selected_mode} of Selected Assets")
    plt.show()
    st.write("Dates avec NaN :")
    st.write(filtered_data[filtered_data.isna().any(axis=1)].index)
    st.pyplot(fig1)

else:
    st.write("Please select at least one asset to display the chart.")

