import streamlit as st
import pandas as pd
import boto3
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(page_title="AWS FinOps Dashboard", layout="wide")

# --- Custom CSS (Baby Pink Theme) ---
st.markdown("""
    <style>
        .stApp {
            background-color: #fff3f6; /* baby pink background */
        }

        section[data-testid="stSidebar"] {
            background-color: #ffe6eb;
        }

        h1, h2, h3, h4 {
            color: #b23a5a;
            font-family: 'Segoe UI', sans-serif;
        }

        p, label, div, span {
            color: #333333 !important;
            font-family: 'Segoe UI', sans-serif;
        }

        .metric-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 20px;
            text-align: center;
        }

        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.title("AWS FinOps Cost Dashboard")
st.write("A visual dashboard for tracking, analyzing, and exporting AWS cost insights over time.")

# --- Sidebar Filters ---
st.sidebar.header("📅 Filters")

end_date = datetime.today()
default_start = end_date - timedelta(days=7)

start = st.sidebar.date_input("Start Date", default_start)
end = st.sidebar.date_input("End Date", end_date)

# --- AWS Client ---
client = boto3.client('ce')

try:
    # Fetch data from AWS Cost Explorer
    response = client.get_cost_and_usage(
        TimePeriod={'Start': start.strftime('%Y-%m-%d'), 'End': end.strftime('%Y-%m-%d')},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    data = []
    for result in response['ResultsByTime']:
        date = result['TimePeriod']['Start']
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])
            data.append({'Date': date, 'Service': service, 'Cost ($)': cost})

    df = pd.DataFrame(data)

    if df.empty:
        st.info("No cost data available for the selected date range.")
    else:
        # --- SERVICE FILTER ---
        services = df["Service"].unique()
        selected_service = st.sidebar.selectbox("AWS Service", ["All"] + list(services))

        if selected_service != "All":
            df = df[df["Service"] == selected_service]

        # --- SUMMARY CARDS ---
        total_cost = df["Cost ($)"].sum()
        avg_cost = df.groupby("Date")["Cost ($)"].sum().mean()
        top_service = df.groupby("Service")["Cost ($)"].sum().idxmax()
        top_cost = df.groupby("Service")["Cost ($)"].sum().max()

        st.subheader("💰 Cost Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <h3>Total Cost</h3>
                    <h2>${total_cost:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <h3>Average Daily Cost</h3>
                    <h2>${avg_cost:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="metric-container">
                    <h3>Top Service</h3>
                    <h2>{top_service}</h2>
                    <p>${top_cost:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

        # --- MONTH-TO-MONTH TREND ---
        st.subheader("📊 Month-to-Month Trend")

        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M")

        monthly_trend = df.groupby("Month")["Cost ($)"].sum()

        fig, ax = plt.subplots()
        ax.plot(monthly_trend.index.astype(str), monthly_trend.values, marker='o', color="#FFB6C1")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Cost ($)")
        ax.set_title("Monthly AWS Cost Trend")
        st.pyplot(fig)

        # --- COST BY SERVICE BAR CHART ---
        st.subheader("Service Cost Breakdown")

        chart_data = df.groupby("Service")["Cost ($)"].sum().sort_values(ascending=False)
        st.bar_chart(chart_data, use_container_width=True)

        # --- DAILY DETAILS TABLE ---
        st.subheader("📅 Daily Details")
        st.dataframe(df, use_container_width=True)

        # --- DOWNLOAD BUTTON ---
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="aws_cost_data.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error("Unable to load data. Please verify your AWS permissions or credentials.")
    st.text(e)
