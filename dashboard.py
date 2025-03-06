!pip install streamlit
import streamlit as st
import pandas as pd
import plotly.express as px

# Set the page config
st.set_page_config(page_title="University Dashboard", layout="wide")

# Title and description
st.title("University Admissions, Retention, and Satisfaction Dashboard")
st.markdown("""
This dashboard monitors key performance indicators across the university’s admissions process, retention rates, and student satisfaction.
Use the filters and interactive charts to explore trends by term, department, and season (Spring vs. Fall).
""")

# Load the data from CSV file
@st.cache_data
def load_data():
    df = pd.read_csv("university_student_dashboard_data.csv")
    # Expected columns: Year, Term, Applications, Admitted, Enrolled, Retention Rate (%), Student Satisfaction (%), Engineering Enrolled, Business Enrolled, Arts Enrolled, Science Enrolled
    # Create a 'season' column based on term name assumptions (e.g., "Spring 2023", "Fall 2023")
    def extract_season(Term):
        if "Spring" in Term:
            return "Spring"
        elif "Fall" in Term:
            return "Fall"
        else:
            return "Other"
    df['season'] = df['Term'].apply(extract_season)
    return df

data = load_data()
st.sidebar.header("Filters")
all_terms = sorted(data['Term'].unique())
selected_term = st.sidebar.selectbox("Select Term", options=["All"] + all_terms)

# Apply filter based on sidebar selection
filtered_data = data.copy()
if selected_term != "All":
    filtered_data = filtered_data[filtered_data['term'] == selected_term]

# Option to preview raw data
if st.sidebar.checkbox("Show Raw Data"):
    st.subheader("Raw Data")
    st.write(filtered_data.head())
# ------------------------------------------------
# Section 1: KPI Summary for the Latest Term
# ------------------------------------------------
st.subheader("Key Performance Indicators (Latest Term)")

# Aggregate metrics per term (summing counts and averaging rates/scores)
term_metrics = data.groupby('Term').agg({
    'Applications': 'sum',
    'Admitted': 'sum',
    'Enrolled': 'sum',
    'Retention Rate (%)': 'mean',
    'Student Satisfaction (%)': 'mean'
}).reset_index()

# Identify the latest term (assuming the sorted order gives the latest term)
latest_term = sorted(term_metrics['Term'])[-1]
latest_data = term_metrics[term_metrics['Term'] == latest_term].iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Applications", int(latest_data['Applications']))
col2.metric("Admitted", int(latest_data['Admitted']))
col3.metric("Enrolled", int(latest_data['Enrolled']))
col4.metric("Avg. Retention Rate", f"{latest_data['Retention Rate (%)']:.2f}")
col5.metric("Avg. Satisfaction Rate", f"{latest_data['Student Satisfaction (%)']:.2f}")
