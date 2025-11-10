# Cross Asset Regime Monitor

This is a financial dashboard that analyzes and visualizes the performance of various asset classes, including equities (SPY), forex (USD), commodities (Gold, Crude Oil, Wheat), and bonds.

## Description

The Cross Asset Regime Monitor is a Python-based application designed for financial market analysis. It provides an interactive dashboard to monitor and visualize the performance of a wide range of asset classes. The application is built with Streamlit and uses Plotly for creating interactive charts.

The project consists of two main parts:
1.  A data processing script (`Market_Dashboard.py`) that downloads historical price data for various assets using the `yfinance` library. It calculates different return metrics and saves the processed data into several `.csv` files.
2.  A web application (`app.py`) built with Streamlit that provides an interactive dashboard. It reads the pre-processed data and allows users to select different assets, timeframes, and calculation modes to view performance charts.

## Features

*   **Multi-Asset Analysis:** Track the performance of various asset classes, including equities, forex, commodities, and bonds.
*   **Interactive Charts:** Visualize asset performance with interactive charts powered by Plotly.
*   **Customizable Timeframes:** Analyze asset performance over different timeframes, from 3 months to 10 years, or a custom date range.
*   **Multiple Calculation Modes:** View asset performance in terms of asset price, linear returns, or logarithmic returns.
*   **Regime Analysis:** Analyze asset performance in different market regimes, such as growth/recession and inflation.
*   **Futures and Options Data:** Visualize the term structure of futures and implied volatility.
*   **Yield Curve Analysis:** Analyze the US yield curve and compare 10-year yields of OECD countries.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Gab1trs/Market-Dashboard.git
    ```
2.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Easiest way** You can follow this link which will directly redirect you on the usable project on streamlit : https://market-dashboard-skema.streamlit.app/

**If you want to do it manually :**

2.  **Data Preparation:** First, run the data download and processing script. This only needs to be done periodically to update the data.
    ```bash
    python Market_Dashboard.py
    ```
3.  **Launch the Dashboard:** Once the data is prepared, run the Streamlit web application.
    ```bash
    streamlit run app.py
    ```
    This will start a local web server and provide a URL to access the interactive dashboard in your browser.

## Data

The application uses historical price data for the following assets:

*   **Equities:** SPY
*   **Forex:** USD
*   **Commodities:** Gold, Crude Oil, Wheat
*   **Bonds:** 10Y T-Bond, Inflation Bond
*   **Volatility:** VIX

The data is downloaded from Yahoo Finance using the `yfinance` library and from the FRED database using `pandas-datareader`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

