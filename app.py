import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title('Option Tool')

# Sidebar for user inputs
st.sidebar.header('Inputs')

# Underlying stock price
underlying_price = st.sidebar.number_input('Underlying Stock Price', min_value=1.0, max_value=1000.0, value=100.0, step=0.1)

# User-defined standard deviation
std_dev = st.sidebar.number_input('Standard Deviation', min_value=0.0, max_value=100.0, value=10.0, step=0.1)

# Dynamic input for multiple option combinations
option_data = []
option_count = st.sidebar.number_input("Number of Option Combinations", min_value=1, max_value=10, value=1, step=1)

for i in range(option_count):
    st.sidebar.subheader(f"Option {i+1}")

    # Option Type and Position
    option_type = st.sidebar.selectbox(f"Option Type {i+1}", ["Call", "Put"])
    position = st.sidebar.selectbox(f"Position {i+1}", ["Long Call", "Short Call"] if option_type == "Call" else ["Long Put", "Short Put"])

    # Quantity, Premium, and Strike Price
    quantity = st.sidebar.number_input(f"Quantity {i+1}", value=1)
    premium = st.sidebar.number_input(f"Premium {i+1}", min_value=0.0, value=5.0, step=0.1)
    strike_price = st.sidebar.number_input(f"Strike Price {i+1}", min_value=0.0, value=100.0, step=0.1)

    option_data.append({
        "option_type": option_type,
        "position": position,
        "quantity": quantity,
        "premium": premium,
        "strike_price": strike_price
    })

# Payoff calculations
def calculate_payoff(stock_price_at_expiry, option):
    if option["option_type"] == "Call":
        if option["position"] == "Long Call":
            return max(stock_price_at_expiry - option["strike_price"], 0) - option["premium"]
        else:  # Short Call
            return min(option["strike_price"] - stock_price_at_expiry, 0) + option["premium"]
    else:
        if option["position"] == "Long Put":
            return max(option["strike_price"] - stock_price_at_expiry, 0) - option["premium"]
        else:  # Short Put
            return min(stock_price_at_expiry - option["strike_price"], 0) + option["premium"]

# Calculate payoffs for a range of stock prices at expiry
upper_bound = underlying_price * (1 + std_dev/100)
lower_bound = underlying_price * (1 - std_dev/100)
stock_prices_at_expiry = np.linspace(lower_bound, upper_bound, 400)
payoffs = [sum([calculate_payoff(price, option) * option["quantity"] for option in option_data]) for price in stock_prices_at_expiry]

# Compute the total for Long options
long_total = sum([option["premium"] * option["quantity"] for option in option_data if "Long" in option["position"]])

# Compute the total for Short options
short_total = sum([option["premium"] * option["quantity"] for option in option_data if "Short" in option["position"]])

# Compute the total cost as the difference
total_cost = long_total - short_total

# Calculate Min and Max Gains
max_gain = max(payoffs)
min_gain = min(payoffs)

# Plotting the net payoff, standard deviation range, and min/max gains
fig = go.Figure()

# Highlight the range for standard deviation
fig.add_shape(
    type="rect",
    x0=underlying_price - std_dev,
    x1=underlying_price + std_dev,
    y0=min(payoffs),
    y1=max(payoffs),
    fillcolor="LightSkyBlue",
    opacity=0.4,
    layer="below",
    line_width=0
)

# Annotations for Max and Min Gains
fig.add_annotation(
    x=stock_prices_at_expiry[payoffs.index(max_gain)],
    y=max_gain,
    xref="x",
    yref="y",
    text="Max Gain",
    showarrow=True,
    arrowhead=4,
    ax=0,
    ay=-40
)

fig.add_annotation(
    x=stock_prices_at_expiry[payoffs.index(min_gain)],
    y=min_gain,
    xref="x",
    yref="y",
    text="Min Gain",
    showarrow=True,
    arrowhead=4,
    ax=0,
    ay=40
)

# Add net payoff line
fig.add_trace(go.Scatter(x=stock_prices_at_expiry, y=payoffs, mode='lines', name='Net Payoff'))

fig.update_layout(title="Payoff Diagram",
                  xaxis_title="Stock Price at Expiry",
                  yaxis_title="Net Payoff",
                  xaxis=dict(showgrid=True),
                  yaxis=dict(showgrid=True))

st.plotly_chart(fig)

# Displaying the total cost to enter the position and Min/Max Gains
st.write(f"Total cost to enter the position: ${total_cost:.0f}")
st.write(f"Maximum Gain: ${max_gain:.0f}")
st.write(f"Minimum Gain (Max Loss): ${min_gain:.0f}")

st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 5px;
            right: 10px;
        }
    </style>
    <div class="footer">Powered by ToxicVolt</div>
    """,
    unsafe_allow_html=True
)

inference = ""

# Define a threshold for what's considered "close" to the underlying price for the Neutral Strategy
threshold = 0.05 * underlying_price  # 5% of the underlying price

# Finding the stock price at which max gain occurs
max_gain_stock_price = stock_prices_at_expiry[payoffs.index(max_gain)]

# Bullish Strategy Inference
if max_gain_stock_price > total_cost:
    inference += "We invest"
elif max_gain_stock_price < total_cost:
    inference += "We dont invest"


if max_gain > total_cost:
    investment_decision = "Invest:  maximum gain exceeds the cost to set up the position."
else:
    investment_decision = "Don't Invest: The setup cost is higher than the  maximum gain."

# skew
if max_gain_stock_price > underlying_price + threshold:
    inference += " Bullish \n"
elif max_gain_stock_price < underlying_price - threshold:
    inference += " Bearish \n"
else:
    inference += " Neutral \n"

st.write(inference)
st.write(investment_decision)