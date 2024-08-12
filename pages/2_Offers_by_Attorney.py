import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, preprocess_data, calculate_offers_by_attorney
import pytz

st.set_page_config(layout="wide")  # Set the layout to wide
st.title("Offers by Attorney")

df = load_data()
df = preprocess_data(df)

# Convert date columns to datetime with UTC timezone
df['offerDate'] = pd.to_datetime(df['offerDate']).dt.tz_convert('UTC')

# Add date and amount input fields for filtering
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=None)
    amount_min = st.number_input("Minimum amount", min_value=0, value=None)
with col2:
    end_date = st.date_input("End date", value=None)
    amount_max = st.number_input("Maximum amount", min_value=0, value=None)

# Convert the start_date and end_date to timezone-aware datetime objects
utc = pytz.UTC
if start_date is not None:
    start_date = utc.localize(pd.to_datetime(start_date))
if end_date is not None:
    end_date = utc.localize(pd.to_datetime(end_date))

# Apply filters based on user input
df_filtered = df.copy()

# Apply date filter if start_date or end_date is not None
if start_date is not None:
    df_filtered = df_filtered[df_filtered['offerDate'] >= start_date]
if end_date is not None:
    df_filtered = df_filtered[df_filtered['offerDate'] <= end_date]

# Apply amount filter if amount_min or amount_max is not None
if amount_min is not None:
    df_filtered = df_filtered[df_filtered['amount'] >= amount_min]
if amount_max is not None:
    df_filtered = df_filtered[df_filtered['amount'] <= amount_max]

# Calculate offers by attorney using the filtered data
offers_by_attorney = calculate_offers_by_attorney(df_filtered)

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
    title=f'Total Offers, Paid Offers, and Unpaid Offers by Attorney'
          f' {f"(From {start_date} " if start_date else ""}'
          f'{f"to {end_date})" if end_date else ")" if start_date else ""}'
          f'{f" Amount: {amount_min} " if amount_min is not None else ""}'
          f'{f" - {amount_max}" if amount_max is not None else ""}',
    xaxis_title='Attorney',
    yaxis_title='Number of Offers',
    barmode='group',
    xaxis_tickangle=-45,
    plot_bgcolor='rgba(0,0,0,0)',
    bargap=0.15,
    bargroupgap=0.1
)

st.plotly_chart(fig, use_container_width=True)