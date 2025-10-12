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
    st.pyplot(fig1)

else:
    st.write("Please select at least one asset to display the chart.")

