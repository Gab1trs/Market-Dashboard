import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from helper import *
from yields import * 

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

#we read all the CSV files with all assets that streamlit will use
data = pd.read_csv("data/all_assets_prices.csv", index_col=0, parse_dates=True)
cpi_data = pd.read_csv("yields/cpi_data.csv", index_col=0, parse_dates=True)
futures= pd.read_csv("futures/all_futures_prices.csv", index_col=0, parse_dates=True)
options=pd.read_csv("options/all_option_chains.csv", index_col=0, parse_dates=True)
yields=pd.read_csv("yields/all_yields.csv", index_col=0, parse_dates=True)
assets = data.columns

data = proxy_global(data)

#we had the inflation regime column to our data
inflation_regime = calculate_realized_inflation_regime(data, cpi_data)
data = data.join(inflation_regime.rename('inflation_regime'))

#this is where we setup all we have in the sidebar
with st.sidebar:
    #first we create the variable that is able to display all the assets at once if needed
    asset_options = ["All Assets"] + assets.tolist()
    selected_options = st.multiselect("Select Assets", asset_options, default=["SPY", "Gold"])
   
    if "All Assets" in selected_options:
        selected_assets = assets.tolist()
    else:
        selected_assets = selected_options

    #here we create the selectbox for the timeframe, the default one is "Max"
    selected_timeframe = st.selectbox("Select Timeframe", ["3m", "6m", "YTD", "1Y", "5Y","10Y", "Max", "Custom"], index=6)

    #depending on the chosen timeframe, we change the strat_date, and thus compute the volatility based on the right timeframe
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
        min_date_dt, max_date_dt = st.date_input("Select Date Range", [data.index.min(), data.index.max()])
        min_date = pd.Timestamp(min_date_dt)
        max_date = pd.Timestamp(max_date_dt)
        filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()
        vol_data = calc_vol(data.loc[min_date-pd.DateOffset(months=6):, selected_assets],min(63, (max_date - min_date).days // 8))
        vol_data = vol_data.loc[min_date:max_date]
    
    #we add two more selectboxes to chose the Mode and the Regime to display
    selected_mode = st.selectbox("Select Mode", ["Asset price", "Linear Returns", "Logarithmic Returns"], index=2)
    selected_regime = st.selectbox("Select Regime to Display", ['Growth/Recession', 'Inflation', 'Both', 'None'])

    #very important line here. Our complete dataframe is bounded to the timeframe previously selected
    mode_data = pd.DataFrame(index=filtered_data.index)

    #now we need to compute the returns for the T-bond and the other assets differently for the reasons we saw in helper.py
    bond_cols = [col for col in selected_assets if col == '10Y T-Bond']
    other_cols = [col for col in selected_assets if col != '10Y T-Bond']

    #depending on the mode selected, we use different functions to compute the returns. Then they are passed into mode_data dataframe
    if selected_mode == "Asset price":
        format_y = ".2f"
        title_y="Asset price"
        mode_data = filtered_data[selected_assets]

    elif selected_mode == "Linear Returns":
        format_y = ".2%"
        title_y="Linear Returns"
        if other_cols:
            other_returns = calc_linear(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='inner')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='linear')
            mode_data = mode_data.join(bond_returns, how='inner')

    elif selected_mode == "Logarithmic Returns":
        format_y = ".2%"
        title_y="Logarithmic Returns"
        if other_cols:
            other_returns = calc_log(filtered_data[other_cols])
            mode_data = mode_data.join(other_returns, how='inner')
        if bond_cols:
            bond_returns = calc_bond_price_returns(filtered_data[bond_cols], mode='log')
            mode_data = mode_data.join(bond_returns, how='inner')
    
    #now this is the part concerning the yields. First, we add again a option that allows us to chose all the countries' yields at the same time
    st.markdown("---")
    yield_options = ["All Yields"] + countries_10Y_yields
    yield_maturities_options = ["All Yields"] + us_yields
    selected__countries_yields = st.multiselect("Select 0ECD 10Y Yields", yield_options, default=["US 10Y", "Germany 10Y"])
    selected__us_treasury_yields = st.multiselect("Select US Treasury Yields", yield_maturities_options, default=["US 3M","US 10Y"])
   
    if "All Yields" in selected__countries_yields:
        selected_yields = countries_10Y_yields
    else:
        selected_yields = selected__countries_yields

    if "All Yields" in selected__us_treasury_yields:
        selected_treasury_yields = us_yields
    else:
        selected_treasury_yields = selected__us_treasury_yields

    selected_yield_timeframe = st.selectbox("Select Yields Timeframe", ["3m", "6m", "YTD", "1Y", "5Y","10Y", "Max", "Custom"], index=6)

    #and again, depending on the second timeframe chosen, we strip our yields dataframe to keep only the interesting values
    if selected_yield_timeframe != "Custom":
        if selected_yield_timeframe == "3m":
            max_date_yields = yields.index.max()
            min_date_yields = max_date_yields - pd.DateOffset(months=3)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "6m":
            max_date_yields = yields.index.max()
            min_date_yields = max_date_yields - pd.DateOffset(months=6)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "YTD":
            max_date_yields = yields.index.max()
            min_date_yields = pd.Timestamp(year=max_date_yields.year, month=1, day=1)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "1Y":
            max_date_yields = yields.index.max()
            min_date_yields = max_date_yields - pd.DateOffset(years=1)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "5Y":
            max_date_yields = yields.index.max()
            min_date_yields = max_date_yields - pd.DateOffset(years=5)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "10Y":
            max_date_yields = yields.index.max()
            min_date_yields = max_date_yields - pd.DateOffset(years=10)
            filtered_data_yields = yields.loc[min_date_yields:, selected_yields] if selected_yields else pd.DataFrame()
            filtered_us_yields=yields.loc[min_date_yields:, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()
        elif selected_yield_timeframe == "Max":
            filtered_data_yields = yields[selected_yields]
            filtered_us_yields=yields[selected_treasury_yields]
    else:
        min_date_yields, max_date_yields = st.date_input("Select Yields Date Range", [yields.index.min(), yields.index.max()])
        filtered_data_yields = yields.loc[min_date_yields:max_date_yields, selected_yields] if selected_yields else pd.DataFrame()
        filtered_us_yields=yields.loc[min_date_yields:max_date_yields, selected_treasury_yields] if selected_treasury_yields else pd.DataFrame()

#now we can begin to plot the results in streamlit
if not filtered_data.empty:
    fig = px.line(
        mode_data,
        x=mode_data.index,
        y=mode_data.columns,
        labels={"value": selected_mode, "variable": "Asset", "index": "Date"},
        title=f"<b>{selected_mode} of Selected Assets</b>"
    )

    #here is the very important part where we display the different regimes
    #first we do some formatting
    if selected_regime == 'Growth/Recession':
        regime_col = 'regime'
        color_map = {'Recession': 'red', 'Growth': 'green'}
        legend_items = [
            {'label': 'Growth', 'color': 'rgb(0,75,0)'},
            {'label': 'Recession', 'color': 'rgb(75,0,0)'}
        ]
    elif selected_regime == 'Inflation':
        regime_col = 'inflation_regime'
        color_map = {'Inflation growth': 'red', 'Inflation decline': 'blue'}
        legend_items = [
            {'label': 'Inflation growth', 'color': 'rgb(75,0,0)'},
            {'label': 'Inflation decline', 'color': 'rgb(0,0,75)'}
        ]
    elif selected_regime == 'Both':
        regime_col = 'both_regimes'
        data['both_regimes'] = data['regime'] + ' & ' + data['inflation_regime'] #we combine both types of regime
        color_map = {
            'Growth & Inflation growth': 'green',
            'Growth & Inflation decline': 'blue',
            'Recession & Inflation growth': 'red',
            'Recession & Inflation decline': 'yellow'
        }
        legend_items = [
            {'label': 'Growth & Inflation growth', 'color': 'rgb(0,75,0)'},
            {'label': 'Growth & Inflation decline', 'color': 'rgb(0,0,75)'},
            {'label': 'Recession & Inflation growth', 'color': 'rgb(75,0,0)'},
            {'label': 'Recession & Inflation decline', 'color': 'rgb(150,150,0)'}
        ]
    else:
        regime_col = None
        legend_items = []

    if regime_col in data.columns:
        regime_series = data[regime_col].dropna()
        change_points = regime_series.ne(regime_series.shift()) #here we identify the points where the regime changes
        period_starts = regime_series.index[change_points] #now we can get all our regime starts

        shapes = []
        for i, start_date in enumerate(period_starts):
            try:
                end_date = period_starts[i+1] #here we define the end our each regime's period
            except IndexError:
                end_date = regime_series.index[-1] #here we deal with the case of the last regime of our data
            
            regime = regime_series[start_date]
            
            if regime in color_map: #this is where we visually represent the regimes on the chart
                shapes.append(
                    dict(
                        type="rect", xref="x", yref="paper",
                        x0=start_date, y0=0, x1=end_date, y1=1,
                        fillcolor=color_map[regime], opacity=0.2, layer="below", line_width=0,
                    )
                )

        visible_shapes = [] #here we prevent the regimes from going outside of the chosen timeframe
        for shape in shapes:
            if shape['x0'] <= max_date and shape['x1'] >= min_date:
                clipped_shape = shape.copy()
                clipped_shape['x0'] = max(shape['x0'], min_date)
                clipped_shape['x1'] = min(shape['x1'], max_date)
                visible_shapes.append(clipped_shape)
    else:
        visible_shapes = []
    
    if selected_regime != 'None': #now we set the legend
        annotations = [
            dict(
                text="<b>Periods</b>", align='left', showarrow=False,
                xref='paper', yref='paper', x=1.02, y=0.5,
                xanchor='left', yanchor='top', font=dict(size=18, family='Arial', color='white')
            )
        ]
    else:
        annotations = []

    y_pos = 0.45
    for item in legend_items: #same here
        annotations.append(
            dict(
                text=f"<span style='color:{item['color']};'>█</span> {item['label']}",
                align='left', showarrow=False, xref='paper', yref='paper',
                x=1.02, y=y_pos, xanchor='left', yanchor='top',
                font=dict(size=18, family='Arial', color='white')
            )
        )
        y_pos -= 0.05

    if selected_regime == 'Inflation' or selected_regime == 'Growth/Recession': #here we set the space that the graph occupies depending on the regime
        r=180
    elif selected_regime == 'None':
        r=80
    else:
        r=280

    fig.update_layout( #and finally here we set up the visual aspect
        shapes=visible_shapes,
        annotations=annotations,
        title=dict(
            text=f"<b>{selected_mode} of Selected Assets</b>",
            x=0.32,
            font=dict(size=22, family='Arial', color='white')
        ),
        legend=dict(
            title=dict(text='<b>Assets</b>', font=dict(size=18, family='Arial', color='white')),
            orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
            font=dict(size=18, family='Arial', color='white')
        ),
        xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16)),
        yaxis=dict(title=title_y, showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=format_y),
        margin=dict(l=40, r=r, t=60, b=40),
        width=1600,
        height=650
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=False)

    if 'VIX' in selected_assets: #in case we chose the VIX asset, we modifiy the title of the next graph
        vol_title='<b>Realized Asset Volatility vs. Implied Market Volatility (VIX)</b>'
        x_pos = 0.26
    else:
        vol_title='<b>Annualized Volatility of Selected Assets</b>'
        x_pos = 0.3

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

    col1, col2 = st.columns(2) #here we split the screen into two columns to display two graphs

    with col1: #here we are goign to plot the futures term structure
        selected_futures_cols = [col for col in selected_assets if col in futures.columns]
        filtered_futures = futures[selected_futures_cols]

        if not filtered_futures.empty:
            
            filtered_futures = filtered_futures.interpolate(method='linear', axis=0) #here we interpolate the missing values so that we don't have cuts in the ploted lines

            fig_futures = px.line(
                filtered_futures,
                x=filtered_futures.index,
                y=filtered_futures.columns,
                labels={"value": "Futures Price", "variable": "Asset", "index": "Date"}
            )
            fig_futures.update_layout(
                title=dict(
                    text="<b>Term Structure of Futures</b>",
                    x=0.22,
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
                xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16), dtick="M6"),
                yaxis=dict(title="Future prices evolution (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2%"),
                margin=dict(l=40, r=120, t=60, b=40),
                height=400
            )
            fig_futures.update_traces(line=dict(width=3))
            st.plotly_chart(fig_futures, use_container_width=True)
        else: #we don't have futures data for the TIP and the VIX so if only those assets are selected we show the text below
            st.markdown('<h3 style="font-size: 22px; color: white;">Term Structure of Futures</h3>', unsafe_allow_html=True) #we use HTML to change the format with plotly
            st.write("No futures term structure data available for the selected asset(s).")

    with col2: #here we are goign to plot the implied volatilty term structure
        selected_options_cols = [col for col in selected_assets if col in options.columns] 
        filtered_options = options[selected_options_cols]

        if not filtered_options.empty:
            
            filtered_options = filtered_options.interpolate(method='linear', axis=0) #here we interpolate the missing values so that we don't have cuts in the ploted lines

            fig_options = px.line(
                filtered_options,
                x=filtered_options.index,
                y=filtered_options.columns,
                labels={"value": "Implied Volatility", "variable": "Asset", "index": "Date"}
            )
            fig_options.update_layout(
                title=dict(
                    text="<b>Term Structure of Implied Volatility</b>",
                    x=0.17,
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
                xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16), dtick="M6"),
                yaxis=dict(title="Implied Volatility (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2%"),
                margin=dict(l=40, r=120, t=60, b=40),
                height=400
            )
            fig_options.update_traces(line=dict(width=3))
            st.plotly_chart(fig_options, use_container_width=True)
        else: #we don't have futures data for the T-Bond so if only this asset is selected we show the text below
            st.markdown('<h3 style="font-size: 22px; color: white;">Term Structure of Implied Volatilty</h3>', unsafe_allow_html=True) #we use HTML to change the format with plotly
            st.write("No volatitly term structure data available for the selected asset.")

    corr=calc_correlation(data)

    fig2 = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale='RdBu', color_continuous_midpoint=0) #here we plot the correlation matrix between all the assets
    fig2.update_layout(
        title=dict(
            text="<b>Correlation between the assets</b>",
            x=0.35,
            font=dict(size=22, family='Arial', color='white')
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
        
    col3, col4 = st.columns(2) #again we split the screen into two columns

    with col3: #here we plot the US yield curve
        yield_curve=get_yield_curve(yields)

        fig_yields = px.line(
                yield_curve,
                x=yield_curve.index,
                y=yield_curve.values,
                labels={"value": "Yield Curve", "variable": "Yield", "index": "Maturities"}
            )
        fig_yields.update_layout(
            title=dict(
                text="<b>US Yield Curve</b>",
                x=0.28,
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
            xaxis=dict(title="Maturities", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16), dtick="M6"),
            yaxis=dict(title="Yield (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2f"),
            margin=dict(l=40, r=120, t=60, b=40),
            height=400
        )
        fig_yields.update_traces(line=dict(width=3))
        st.plotly_chart(fig_yields, use_container_width=True)

    with col4: #here we will plot the chart of the evolution of the 10Y yields of the OECD countries
        countries_yields=get_countries_yields(yields)

        fig_countries_yields = px.bar(
                countries_yields,
                x=countries_yields.index,
                y=countries_yields.values,
                labels={"value": "Countries 10Y Yields Curve", "variable": "Yield", "index": "Maturities"}
            )
        fig_countries_yields.update_layout(
            title=dict(
                text="<b>OECD countries 10Y Yield Curve</b>",
                x=0.2,
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
            xaxis=dict(title="Countries", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16), dtick="M6"),
            yaxis=dict(title="10Y Yields (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2f"),
            margin=dict(l=40, r=80, t=60, b=40),
            height=400
        )
        st.plotly_chart(fig_countries_yields, use_container_width=True)
    
    col5, col6 = st.columns(2) #again we split the screen into two columns

    with col5: #here we will plot the timeframe adjusted OECD 10Y yields chart

        fig_yields_OECD = px.line(
                filtered_data_yields,
                labels={"value": "Yield Curve", "variable": "Yield", "index": "Date"}
            )
        fig_yields_OECD.update_layout(
            title=dict(
                text="<b>OEDC 10Y Yields Over Time</b>",
                x=0.22,
                font=dict(size=22, family='Arial', color='white')
            ),
            legend=dict(
                title=dict(text='<b>Yields</b>', font=dict(size=18, family='Arial', color='white')),
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                font=dict(size=18, family='Arial', color='white')
            ),
            xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16)),
            yaxis=dict(title="Yield (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2f"),
            margin=dict(l=40, r=120, t=60, b=40),
            height=400
        )
        fig_yields_OECD.update_traces(line=dict(width=3))
        st.plotly_chart(fig_yields_OECD, use_container_width=True)

    with col6: #here we will plot the timeframe adjusted US yields chart

        fig_yields_us= px.line(
                filtered_us_yields,
                labels={"value": "Yield Curve", "variable": "Yield", "index": "Date"}
            )
        fig_yields_us.update_layout(
            title=dict(
                text="<b>US Treasury Yields Over Time</b>",
                x=0.22,
                font=dict(size=22, family='Arial', color='white')
            ),
            legend=dict(
                title=dict(text='<b>Yields</b>', font=dict(size=18, family='Arial', color='white')),
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02,
                font=dict(size=18, family='Arial', color='white')
            ),
            xaxis=dict(title="Date", showgrid=True, gridcolor="#eee", tickangle=0, title_font=dict(size=16)),
            yaxis=dict(title="Yield (%)", showgrid=True, gridcolor="#eee", title_font=dict(size=16), tickformat=".2f"),
            margin=dict(l=40, r=120, t=60, b=40),
            height=400
        )
        fig_yields_us.update_traces(line=dict(width=3))
        st.plotly_chart(fig_yields_us, use_container_width=True)


else:
    st.write("Please select at least one asset to display the chart.")

