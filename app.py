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
cpi_data = pd.read_csv("data/cpi_data.csv", index_col=0, parse_dates=True)
assets = data.columns

data = proxy_global(data)

inflation_regime = calculate_realized_inflation_regime(data, cpi_data)
data = data.join(inflation_regime.rename('inflation_regime'))

with st.sidebar:
    selected_assets = st.multiselect("Select Assets", assets,  default=["SPY"])
    selected_timeframe = st.selectbox("Select Timeframe", ["3m", "6m", "YTD", "1Y", "5Y","10Y", "Max", "Custom"], index=6)

    if selected_timeframe != "Custom":
        if selected_timeframe == "3m":
            max_date = data.index.max()
            min_date = max_date - pd.DateOffset(months=3)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=1):, selected_assets], 10)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "6m":
            max_date = data.index.max()
            min_date = max_date - pd.DateOffset(months=6)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "YTD":
            max_date = data.index.max()
            min_date = pd.Timestamp(year=max_date.year, month=1, day=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "1Y":
            max_date = data.index.max()
            min_date = max_date - pd.DateOffset(years=1)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=2):, selected_assets], 21)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "5Y":
            max_date = data.index.max()
            min_date = max_date - pd.DateOffset(years=5)
            filtered_data = data.loc[min_date:, selected_assets] if selected_assets else pd.DataFrame()
            vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets], 63)
            vol_data = vol_data.loc[min_date:]
        elif selected_timeframe == "10Y":
            max_date = data.index.max()
            min_date = max_date - pd.DateOffset(years=10)
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
        vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets],min(63, (max_date - min_date).days // 8))
        vol_data = vol_data.loc[min_date:max_date]
    
    selected_mode = st.selectbox("Select Mode", ["Asset price", "Linear Returns", "Logarithmic Returns"])
    selected_regime = st.selectbox("Select Regime to Display", ['Growth/Recession', 'Inflation'])

    mode_data = pd.DataFrame(index=filtered_data.index)

    bond_cols = [col for col in selected_assets if col == '10Y T-Bond']
    other_cols = [col for col in selected_assets if col != '10Y T-Bond']

    if selected_mode == "Asset price":
        mode_data = filtered_data[selected_assets]

    elif selected_mode == "Linear Returns":
        if other_cols:
            other_returns = calc_linear(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='inner')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='linear')
            mode_data = mode_data.join(bond_returns, how='inner')

    elif selected_mode == "Logarithmic Returns":
        if other_cols:
            other_returns = calc_log(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='inner')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='log')
            mode_data = mode_data.join(bond_returns, how='inner')


if not filtered_data.empty:
    fig = px.line(
        mode_data,
        x=mode_data.index,
        y=mode_data.columns,
        labels={"value": selected_mode, "variable": "Asset", "index": "Date"},
        title=f"<b>{selected_mode} of Selected Assets</b>"
    )

    # --- DYNAMIC REGIME SHAPES AND LEGEND ---

    # 1. Determine which regime column and color mapping to use
    if selected_regime == 'Growth/Recession':
        regime_col = 'regime'
        color_map = {'Recession': 'red', 'Growth': 'green'}
        legend_items = [
            {'label': 'Growth', 'color': 'rgb(0,75,0)'},
            {'label': 'Recession', 'color': 'rgb(75,0,0)'}
        ]
    else: # Inflation
        regime_col = 'inflation_regime'
        color_map = {'Inflation en Hausse': 'red', 'Inflation en Baisse': 'blue'}
        legend_items = [
            {'label': 'Inflation en Hausse', 'color': 'rgb(75,0,0)'},
            {'label': 'Inflation en Baisse', 'color': 'rgb(0,0,75)'}
        ]

    # 2. Find the periods for the selected regime
    if regime_col in data.columns:
        regime_series = data[regime_col].dropna()
        change_points = regime_series.ne(regime_series.shift())
        period_starts = regime_series.index[change_points]

        shapes = []
        for i, start_date in enumerate(period_starts):
            try:
                end_date = period_starts[i+1]
            except IndexError:
                end_date = regime_series.index[-1]
            
            regime = regime_series[start_date]
            
            if regime in color_map:
                shapes.append(
                    dict(
                        type="rect", xref="x", yref="paper",
                        x0=start_date, y0=0, x1=end_date, y1=1,
                        fillcolor=color_map[regime], opacity=0.2, layer="below", line_width=0,
                    )
                )

        # 3. Filter shapes to the visible date range
        visible_shapes = []
        for shape in shapes:
            if shape['x0'] <= max_date and shape['x1'] >= min_date:
                clipped_shape = shape.copy()
                clipped_shape['x0'] = max(shape['x0'], min_date)
                clipped_shape['x1'] = min(shape['x1'], max_date)
                visible_shapes.append(clipped_shape)
    else:
        visible_shapes = []

    # 4. Create the dynamic legend annotations
    annotations = [
        dict(
            text="<b>Periods</b>", align='left', showarrow=False,
            xref='paper', yref='paper', x=1.02, y=0.5,
            xanchor='left', yanchor='top', font=dict(size=18, family='Arial', color='white')
        )
    ]
    y_pos = 0.45
    for item in legend_items:
        annotations.append(
            dict(
                text=f"<span style='color:{item['color']};'>█</span> {item['label']}",
                align='left', showarrow=False, xref='paper', yref='paper',
                x=1.02, y=y_pos, xanchor='left', yanchor='top',
                font=dict(size=18, family='Arial', color='white')
            )
        )
        y_pos -= 0.05

    # 5. Update the figure
    fig.update_layout(
        shapes=visible_shapes,
        annotations=annotations,
        title=dict(
            text=f"<b>{selected_mode} of Selected Assets</b>",
            x=0.28,
            font=dict(size=22, family='Arial', color='white')
        ),
        legend=dict(
            title=dict(text='<b>Assets</b>', font=dict(size=18, family='Arial', color='white')),
            orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
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
        x_pos = 0.21
    else:
        vol_title='<b>Annualized Volatility of Selected Assets</b>'
        x_pos = 0.28

    fig1 = px.line(
        vol_data,
        x=vol_data.index,
        y=vol_data.columns,
        labels={"value": "Volatility", "variable": "Asset", "index": "Date"}
    )
    fig1.update_layout(
        title=dict(
            text=vol_title,
            x=x_pos,
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

