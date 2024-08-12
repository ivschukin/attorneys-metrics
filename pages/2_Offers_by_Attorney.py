import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, preprocess_data, calculate_offers_by_attorney

st.set_page_config(layout="wide")  # Set the layout to wide
st.title("Offers by Attorney")

df = load_data()
df = preprocess_data(df)

offers_by_attorney = calculate_offers_by_attorney(df)

# Create a grouped bar chart using Plotly
fig = go.Figure()

fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['total_offers'],
    name='Total Offers',
    marker=dict(color='blue')
))

fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['paid_offers'],
    name='Paid Offers',
    marker=dict(color='green')
))

fig.add_trace(go.Bar(
    x=offers_by_attorney['offeredby'],
    y=offers_by_attorney['unpaid_offers'],
    name='Unpaid Offers',
    marker=dict(color='red')
))

fig.update_layout(
    title='Total Offers, Paid Offers, and Unpaid Offers by Attorney',
    xaxis_title='Attorney',
    yaxis_title='Number of Offers',
    barmode='group',
    xaxis_tickangle=-45,
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.15,
    bargroupgap=0.1
)

st.plotly_chart(fig, use_container_width=True)
