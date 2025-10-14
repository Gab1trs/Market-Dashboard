import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from Market_Dashboard import startdate
import plotly.express as px
import numpy as np
from helper import * 

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

data = pd.read_csv("data/all_assets_prices.csv", index_col=0, parse_dates=True)
assets = data.columns

with st.sidebar:
    selected_assets = st.multiselect("Select Assets", assets,  default=["SPY"])
    selected_timeframe = st.selectbox("Select Timeframe", ["3m", "6m", "YTD", "1Y", "5Y","10Y", "Max", "Custom"], index=6)

    if selected_timeframe != "Custom":
        if selected_timeframe == "3m":
            min_date = data.index.max() - pd.DateOffset(months=3)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "6m":
            min_date = data.index.max() - pd.DateOffset(months=6)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "YTD":
            min_date = pd.Timestamp(year=data.index.max().year, month=1, day=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "1Y":
            min_date = data.index.max() - pd.DateOffset(years=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "5Y":
            min_date = data.index.max() - pd.DateOffset(years=5)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "10Y":
            min_date = data.index.max() - pd.DateOffset(years=10)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
        elif selected_timeframe == "Max":
            min_date = data.index.min()
            max_date = data.index.max()
            filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()  
    else:
        min_date, max_date = st.date_input("Select Date Range", [data.index.min(), data.index.max()])
        filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()
    
    selected_mode = st.selectbox("Select Mode", ["Asset price", "Linear Returns", "Logarithmic Returns"])

    if selected_mode == "Asset price":
        mode_data = filtered_data
    elif selected_mode == "Linear Returns":
        mode_data = calc_linear(filtered_data)
    elif selected_mode == "Logarithmic Returns":
        mode_data = calc_log(filtered_data)


if not filtered_data.empty:
    # If using matplotlib
    # plt.style.use("seaborn-v0_8-darkgrid")
    # fig = plt.figure(figsize=(12,7))
    # plt.plot(filtered_data, linewidth=2)
    # plt.xlim(filtered_data.index.min())
    # plt.xlabel("Date", fontsize=14)
    # plt.ylabel(selected_mode, fontsize=14)
    # plt.title(f"{selected_mode} of Selected Assets", fontsize=16, fontweight="bold")
    # plt.grid(True, linestyle='--', alpha=0.5)
    # plt.legend(selected_assets, fontsize=12, loc='upper left')
    # fig.autofmt_xdate()
    # plt.tight_layout()

    # If using Plotly
    fig = px.line(
        mode_data,
        x=mode_data.index,
        y=mode_data.columns,
        labels={"value": selected_mode, "variable": "Asset", "index": "Date"},
        title=f"<b>{selected_mode} of Selected Assets</b>"
    )
    fig.update_layout(
        title=dict(
            text=f"<b>{selected_mode} of Selected Assets</b>",
            x=0.32,
            font=dict(size=22, family='Arial', color='white')
        ),
        legend=dict(
            title=dict(text='<b>Assets</b>', font=dict(size=18, family='Arial', color='white')),
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=18, family='Arial', color='white')
        ),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16)),
        yaxis=dict(title=selected_mode, showgrid=True, gridcolor="#eee", title_font=dict(size=16)),
        margin=dict(l=40, r=120, t=60, b=40),
        width=1600,
        height=650
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=False)

else:
    st.write("Please select at least one asset to display the chart.")

