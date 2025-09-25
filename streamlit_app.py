import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

title = "Cross Asset Regime Monitor"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

data=pd.read_csv('all_assets.csv', index_col=0, parse_dates=True)
assets=data.columns

with st.sidebar:
    selected_assets=st.multiselect("Select Assets", assets)
    min_date, max_date=st.date_input("Select Date Range", [data.index.min(), data.index.max()])

# Filter data by date and selected assets
filtered_data = data.loc[min_date:max_date, selected_assets] if selected_assets else pd.DataFrame()

if not filtered_data.empty:
    fig1=plt.figure(figsize=(10,6))
    plt.plot(filtered_data)
    plt.legend(selected_assets)
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.title("Cumulative Returns of All Assets")
    plt.show()
    st.pyplot(fig1)

else:
    st.write("Please select at least one asset to display the chart.")

