import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery

query = "SELECT * FROM `lexense-odr.lexense.custom_offers_analysis`"

@st.cache_data
def load_data():
    client = bigquery.Client()
    df = client.query(query).to_dataframe()

    return df

def main():
    st.title("BigQuery Data Analysis in Streamlit")

    # Load data
    df = load_data()

    st.write("Data loaded successfully!")

    # Display some data
    st.write(df.head())

    # Example histogram
    st.subheader("Distribution of Order Amounts")
    plt.figure(figsize=(10, 6))
    plt.hist(df['amount'], bins=30, edgecolor='k', alpha=0.7)
    plt.title('Distribution of Order Amounts')
    plt.xlabel('Order Amount')
    plt.ylabel('Frequency')
    st.pyplot(plt)

if __name__ == "__main__":
    main()
