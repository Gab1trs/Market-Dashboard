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
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=1):, selected_assets], 10)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "6m":
            min_date = data.index.max() - pd.DateOffset(months=6)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "YTD":
            min_date = pd.Timestamp(year=data.index.max().year, month=1, day=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "1Y":
            min_date = data.index.max() - pd.DateOffset(years=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "5Y":
            min_date = data.index.max() - pd.DateOffset(years=5)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets], 63)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "10Y":
            min_date = data.index.max() - pd.DateOffset(years=10)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets], 63)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "Max":
            min_date = data.index.min()
            max_date = data.index.max()
            filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date:, selected_assets], 63)
            vol_data = vol_data.loc[min_date:]
    else:
        min_date, max_date = st.date_input("Select Date Range", [data.index.min(), data.index.max()])
        filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()
        vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets], max(63, (max_date - min_date).days // 8))
        vol_data = vol_data.loc[min_date:max_date]
    
    selected_mode = st.selectbox("Select Mode", ["Asset price", "Linear Returns", "Logarithmic Returns"])

    mode_data = pd.DataFrame(index=filtered_data.index)

    # Separate bond columns from other assets
    bond_cols = [col for col in selected_assets if col == '10Y T-Bond']
    other_cols = [col for col in selected_assets if col != '10Y T-Bond']

    if selected_mode == "Asset price":
        if not filtered_data.empty:
            mode_data = filtered_data[selected_assets]

    elif selected_mode == "Linear Returns":
        if other_cols:
            other_returns = calc_linear(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='outer')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='linear')
            mode_data = mode_data.join(bond_returns, how='outer')

    elif selected_mode == "Logarithmic Returns":
        if other_cols:
            other_returns = calc_log(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='outer')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='log')
            mode_data = mode_data.join(bond_returns, how='outer')


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

    if 'VIX' in selected_assets:
        vol_title='<b>Realized Asset Volatility vs. Implied Market Volatility (VIX)</b>'
    else:
        vol_title='<b>Annualized Volatility of Selected Assets</b>'

    fig1 = px.line(
        vol_data,
        x=vol_data.index,
        y=vol_data.columns,
        labels={"value": "Volatility", "variable": "Asset", "index": "Date"}
    )
    fig1.update_layout(
        title=dict(
            text=vol_title,
            x=0.29,
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
        yaxis=dict(title="Volatility", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".0%"),
        margin=dict(l=40, r=120, t=60, b=40),
        width=1600,
        height=650
    )
    fig1.update_traces(line=dict(width=3))
    st.plotly_chart(fig1, use_container_width=False)

else:
    st.write("Please select at least one asset to display the chart.")

