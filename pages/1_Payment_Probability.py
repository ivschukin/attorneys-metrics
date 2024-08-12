import streamlit as st
from utils import load_data, preprocess_data, calculate_payment_probability
import plotly.graph_objects as go

st.set_page_config(layout="wide")  # Set the layout to wide
st.title("Payment Probability by Order Amount Range")

df = load_data()
df = preprocess_data(df)

payment_prob = calculate_payment_probability(df)  # Reuse the calculate_payment_probability function

# Plotting code (e.g., Plotly code from before)

# Create a Plotly bar chart for payment probability
fig = go.Figure()

fig.add_trace(go.Bar(
    x=payment_prob['amount_range'],
    y=payment_prob['payment_probability'],
    text=[f'Offers: {row["total_offers"]}<br>Paid: {row["paid_offers"]}' for _, row in payment_prob.iterrows()],
    textposition='auto',
    marker=dict(color='skyblue'),
    name='Payment Probability'
))

fig.update_layout(
    title='Payment Probability by Order Amount Range',
    xaxis_title='Order Amount Range',
    yaxis_title='Payment Probability',
    yaxis=dict(range=[0, 1.1]),
    bargap=0.1,
    plot_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig, use_container_width=True)
