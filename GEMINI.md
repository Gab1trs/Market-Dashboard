# GEMINI Project Analysis: Market-Dashboard

## Project Overview

This project is a Python-based financial dashboard called the "Cross Asset Regime Monitor". It is designed to analyze and visualize the performance of various asset classes, including equities (SPY), forex (USD), commodities (Gold, Crude Oil, Wheat), and bonds.

The application consists of two main parts:
1.  A data processing script (`Market_Dashboard.py`) that uses the `yfinance` library to download historical price data for the specified assets. It then calculates different return metrics (linear and logarithmic) and saves the processed data into several `.csv` files (`all_assets_prices.csv`, `all_assets_linear.csv`, `all_assets_log.csv`).
2.  A web application (`app.py`) built with Streamlit. This app provides an interactive dashboard that reads the pre-processed data from `all_assets_prices.csv`. Users can select different assets, timeframes, and calculation modes (Asset Price, Linear, Logarithmic) to view performance charts generated with Plotly.

The helper script `helper.py` contains the core logic for data downloading and financial calculations.

## Building and Running

There is no formal `requirements.txt` file, but based on the source code, the following Python libraries are required:
- `streamlit`
- `pandas`
- `yfinance`
- `plotly`
- `numpy`
- `matplotlib`

**TODO:** A `requirements.txt` file should be created for easier dependency management. A good starting point would be:
```
streamlit
pandas
yfinance
plotly
numpy
matplotlib
```

### Running the Application

The application is run in two stages:

1.  **Data Preparation:** First, run the data download and processing script. This only needs to be done periodically to update the data.
    ```bash
    python Market_Dashboard.py
    ```

2.  **Launch the Dashboard:** Once the data is prepared, run the Streamlit web application.
    ```bash
    streamlit run app.py
    ```
    This will start a local web server and provide a URL to access the interactive dashboard in your browser.

## Development Conventions

*   **Data Flow:** The application follows a two-step process where data is first fetched and stored locally in CSV files, and then the web application consumes this local data. This decouples the data fetching from the user-facing application, which improves performance and resilience against API failures.
*   **Configuration:** Asset tickers are defined in a dictionary within `Market_Dashboard.py`.
*   **Visualization:** The application uses the Plotly library for creating interactive charts, which is a good choice for modern web-based dashboards. There is commented-out Matplotlib code, suggesting a potential shift during development.
*   **Modularity:** Core, reusable functions are separated into `helper.py`, which is good practice.
