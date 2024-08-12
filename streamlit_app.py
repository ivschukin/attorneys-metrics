import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from google.oauth2 import service_account
import re
import json5
import ast

# Load the secret from Streamlit's secrets management
raw_json_str = st.secrets["general"]["GOOGLE_APPLICATION_CREDENTIALS"]

def smart_json_parser(raw_json_str):
    try:
        parsed_json = json5.loads(raw_json_str)
        return parsed_json
    except Exception as e:
        cleaned_json_str = raw_json_str.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
        cleaned_json_str = re.sub(r'\\', '', cleaned_json_str)

        try:
            parsed_json = ast.literal_eval(cleaned_json_str)
            return parsed_json
        except Exception as eval_error:
            try:
                parsed_json = json.loads(cleaned_json_str)
                return parsed_json
            except Exception as json_error:
                raise ValueError(
                    f"Failed to parse JSON: {json_error}\nOriginal Error: {e}\nEvaluation Error: {eval_error}")


service_account_info = smart_json_parser(raw_json_str)
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

@st.cache_data
def load_data():
    query = """SELECT * FROM `lexense-odr.lexense.custom_offers_analysis`"""
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
