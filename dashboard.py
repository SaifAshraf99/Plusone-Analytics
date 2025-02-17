import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Function to load and process data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Explicitly convert date columns
    date_cols = [
        'create_date', 'submit_history_date', 'first_sent_to_expert_date', 
        'final_opinion_date', 'close_date', 'follow_up_date'
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert, setting invalid ones to NaT

    return df

# Streamlit UI
st.title("📊 Case Processing Dashboard: PlusOne & Gustave Time")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)

    # Sidebar: Column Selection for PlusOne & Gustave Time
    st.sidebar.header("🔧 Select Processing Time Fields")

    plusone_start = st.sidebar.selectbox("Select Start Date for PlusOne Time", df.columns, index=df.columns.get_loc('submit_history_date'))
    plusone_end = st.sidebar.selectbox("Select End Date for PlusOne Time", df.columns, index=df.columns.get_loc('first_sent_to_expert_date'))

    gustave_start = st.sidebar.selectbox("Select Start Date for Gustave Time", df.columns, index=df.columns.get_loc('first_sent_to_expert_date'))
    gustave_end = st.sidebar.selectbox("Select End Date for Gustave Time", df.columns, index=df.columns.get_loc('final_opinion_date'))

    # Ensure selected columns are datetime
    df[plusone_start] = pd.to_datetime(df[plusone_start], errors='coerce')
    df[plusone_end] = pd.to_datetime(df[plusone_end], errors='coerce')
    df[gustave_start] = pd.to_datetime(df[gustave_start], errors='coerce')
    df[gustave_end] = pd.to_datetime(df[gustave_end], errors='coerce')

    # Compute custom time differences
    df['plusone_time'] = (df[plusone_end] - df[plusone_start]).dt.days
    df['gustave_time'] = (df[gustave_end] - df[gustave_start]).dt.days

    # 📊 1️⃣ Bar Chart: PlusOne Time vs Gustave Time
    st.subheader("⏳ Case Processing: PlusOne vs Gustave Time")
    fig_bar = go.Figure()

    # Add PlusOne Time Bars
    fig_bar.add_trace(go.Bar(
        x=df['name'],  
        y=df['plusone_time'],
        name="PlusOne Time",
        marker_color="blue"
    ))

    # Add Gustave Time Bars
    fig_bar.add_trace(go.Bar(
        x=df['name'],  
        y=df['gustave_time'],
        name="Gustave Time",
        marker_color="orange"
    ))

    # Set Y-axis range
    fig_bar.update_yaxes(range=[0, 50], dtick=5)

    # Show the Bar Chart
    st.plotly_chart(fig_bar, use_container_width=True)

    # 📊 2️⃣ Pie Chart: PlusOne Time Distribution
    st.subheader("📊 Distribution of PlusOne Time")

    bins = list(range(0, 55, 5))
    labels = [f"{i}-{i+4} days" for i in bins[:-1]] + ["50+ days"]
    df['plusone_bucket'] = pd.cut(df['plusone_time'], bins=bins + [float("inf")], labels=labels, right=False)

    fig_pie_plusone = px.pie(df, names="plusone_bucket", title="Number of Cases per PlusOne Time Range")
    st.plotly_chart(fig_pie_plusone, use_container_width=True)

    # 📊 3️⃣ Pie Chart: Gustave Time Distribution
    st.subheader("📊 Distribution of Gustave Time")

    df['gustave_bucket'] = pd.cut(df['gustave_time'], bins=bins + [float("inf")], labels=labels, right=False)

    fig_pie_gustave = px.pie(df, names="gustave_bucket", title="Number of Cases per Gustave Time Range")
    st.plotly_chart(fig_pie_gustave, use_container_width=True)

    # 📊 4️⃣ Scatter Plot: PlusOne Time vs Gustave Time
    st.subheader("📊 PlusOne Time vs Gustave Time")

    fig_scatter = px.scatter(df, x="plusone_time", y="gustave_time", title="PlusOne Time vs Gustave Time")
    st.plotly_chart(fig_scatter, use_container_width=True)
