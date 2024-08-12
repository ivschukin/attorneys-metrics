import streamlit as st
import json
import matplotlib.pyplot as plt
from google.cloud import bigquery
from google.oauth2 import service_account
import re
import json5
import ast
import pandas as pd
import numpy as  np
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_data():
    query = """SELECT * FROM `lexense-odr.lexense.custom_offers_analysis`"""
    df = client.query(query).to_dataframe()
    return df

st.title("Attorney Metrics - Dashboard")

df = load_data()
df = df.dropna(subset=['amount', 'isPaid', 'scopeestimatedtime'])

df['amount_range'] = pd.cut(df['amount'], bins=[0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, df['amount'].max()],
                            labels=['0-100', '100-200', '200-300', '300-400', '400-500', '500-600', '600-700', '700-800', '800-900', '900-1000', '1000-1100', '1100-1200', '1200+'])
df['offerDate'] = pd.to_datetime(df['offerDate'])
df['paymentDate'] = pd.to_datetime(df['paymentDate'])
df['days_to_buy'] = (df['paymentDate'] - df['offerDate']).dt.days

df_paid = df[df['isPaid'] == True]
df_unpaid = df[df['isPaid'] != True]

payment_prob = calculate_payment_probability(df)



# Create a Plotly bar chart
fig = go.Figure()

# Add bars for payment probability
fig.add_trace(go.Bar(
    x=payment_prob['amount_range'],
    y=payment_prob['payment_probability'],
    text=[f'Offers: {row["total_offers"]}<br>Paid: {row["paid_offers"]}' for _, row in payment_prob.iterrows()],
    textposition='auto',
    marker=dict(color='skyblue'),
    name='Payment Probability'
))

# Customize the layout
fig.update_layout(
    title='Payment Probability by Order Amount Range',
    xaxis_title='Order Amount Range',
    yaxis_title='Payment Probability',
    yaxis=dict(range=[0, 1.1]),  # Extend y-axis to make space for annotations
    bargap=0.1,
    plot_bgcolor='rgba(0,0,0,0)',
)

# Display the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)


offers_by_attorney = calculate_offers_by_attorney(df)

# Create a grouped bar chart using Plotly
fig = go.Figure()

# Bar for total offers
fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['total_offers'],
    name='Total Offers',
    marker=dict(color='blue')
))

# Bar for paid offers
fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['paid_offers'],
    name='Paid Offers',
    marker=dict(color='green')
))

# Bar for unpaid offers
fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['unpaid_offers'],
    name='Unpaid Offers',
    marker=dict(color='red')
))

# Customize the layout
fig.update_layout(
    title='Total Offers, Paid Offers, and Unpaid Offers by Attorney',
    xaxis_title='Attorney',
    yaxis_title='Number of Offers',
    barmode='group',  # Group the bars
    xaxis_tickangle=-45,  # Rotate x-axis labels
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
    bargap=0.15,  # Gap between bars
    bargroupgap=0.1  # Gap between groups of bars
)

# Display the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)
