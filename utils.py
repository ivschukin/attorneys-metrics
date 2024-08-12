import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import re
import ast
import streamlit as st
import json5
import json

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


raw_json_str = st.secrets["general"]["GOOGLE_APPLICATION_CREDENTIALS"]
service_account_info = smart_json_parser(raw_json_str)

credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def calculate_payment_probability(df):
    # Group by amount_range and calculate payment probability
    payment_prob = df.groupby('amount_range').agg(
        total_offers=('amount', 'count'),
        paid_offers=('isPaid', 'sum')
    ).reset_index()

    # Calculate payment probability
    payment_prob['payment_probability'] = payment_prob['paid_offers'] / payment_prob['total_offers']

    return payment_prob

# Assuming df is already loaded and processed
def calculate_offers_by_attorney(df):
    # Group by attorney and calculate total, paid, and unpaid offers
    offers_by_attorney = df.groupby('offeredby').agg(
        total_offers=('isPaid', 'size'),
        paid_offers=('isPaid', 'sum')
    ).reset_index()

    # Calculate unpaid offers
    offers_by_attorney['unpaid_offers'] = offers_by_attorney['total_offers'] - offers_by_attorney['paid_offers']

    return offers_by_attorney

# Function to load data from BigQuery
def load_data():
    query = """SELECT * FROM `lexense-odr.lexense.custom_offers_analysis`"""
    df = client.query(query).to_dataframe()

    return df

def preprocess_data(df):
    df = df.dropna(subset=['amount', 'isPaid', 'scopeestimatedtime'])

    df['amount_range'] = pd.cut(df['amount'], bins=[0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200,
                                                    df['amount'].max()],
                                labels=['0-100', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700',
                                        '700-800', '800-900', '900-1000', '1000-1100', '1100-1200', '1200+'])
    df['offerDate'] = pd.to_datetime(df['offerDate'])
    df['paymentDate'] = pd.to_datetime(df['paymentDate'])
    df['days_to_buy'] = (df['paymentDate'] - df['offerDate']).dt.days

    return df
