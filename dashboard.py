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
    filtered_data = filtered_data[filtered_data['Term'] == selected_term]

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
col5.metric("Avg. Satisfaction", f"{latest_data['Student Satisfaction (%)']:.2f}")

# Section 2: Trend Analysis Over Terms
# ------------------------------------------------
st.subheader("Trend Analysis Over Terms")

# Plot line chart for Applications, Admissions, and Enrollments
fig_admissions = px.line(term_metrics,
                         x='Term', 
                         y=['Applications', 'Admitted', 'Enrolled'],
                         markers=True,
                         title="Applications, Admissions, and Enrollments Over Terms")
st.plotly_chart(fig_admissions, use_container_width=True)

# Plot line chart for Retention Rate over time
fig_retention = px.line(term_metrics,
                        x='Term', 
                        y='Retention Rate (%)',
                        markers=True,
                        title="Average Retention Rate Over Terms")
st.plotly_chart(fig_retention, use_container_width=True)

# Plot line chart for Satisfaction Score over time
fig_satisfaction = px.line(term_metrics,
                           x='Term', 
                           y='Student Satisfaction (%)',
                           markers=True,
                           title="Average Student Satisfaction Over Terms")
st.plotly_chart(fig_satisfaction, use_container_width=True)

# ------------------------------------------------
# Section 3: Seasonal (Spring vs. Fall) Analysis
# ------------------------------------------------
st.subheader("Seasonal Analysis: Spring vs. Fall")

# Group data by season and aggregate metrics
season_metrics = data.groupby('season').agg({
    'Applications': 'sum',
    'Admitted': 'sum',
    'Enrolled': 'sum',
    'Retention Rate (%)': 'mean',
    'Student Satisfaction (%)': 'mean'
}).reset_index()

fig_season = px.bar(season_metrics,
                    x='season',
                    y=['Applications', 'Admitted', 'Enrolled'],
                    barmode='group',
                    title="Seasonal Comparison: Applications, Admissions, and Enrollments")
st.plotly_chart(fig_season, use_container_width=True)

# ------------------------------------------------
# Section 4: Interpretations and Insights
# ------------------------------------------------
st.subheader("Interpretations and Insights")
st.markdown("""
- **Admissions Trends:**  
  The trend charts show how applications, admissions, and enrollments have changed over different terms. Sudden peaks or declines may reflect the impact of recruitment initiatives, modifications to admission criteria, or broader economic and social factors.
  
- **Retention Rates:**  
  Stable or improving retention rates generally indicate effective academic support and student services. A decline in retention, particularly during specific terms, may signal challenges such as curriculum difficulties or insufficient student engagement.
  
- **Satisfaction Scores:**  
  Trends in student satisfaction provide key insights into the overall student experience. If lower satisfaction scores coincide with drops in retention, it underscores the need to invest in quality teaching, enhanced support services, and improved campus facilities.
  
- **Seasonal Differences:**  
  Analyzing metrics by season (Spring vs. Fall) can reveal distinct patterns. For example, higher application and enrollment numbers in the Fall term might align with the high school graduation cycle, whereas the Spring term could attract a different student profile.
  
- **Correlation Insights:**  
  The dashboard also allows for exploring potential correlations between satisfaction and retention. A strong positive correlation would suggest that efforts to improve the student experience could directly enhance retention rates.
  
- **Actionable Strategies:**  
  - **Resource Allocation:** Focus on terms with lower retention and satisfaction for targeted interventions such as improved academic advising or mentorship programs.  
  - **Recruitment Tactics:** Adapt recruitment strategies based on seasonal trends to ensure a balanced and diverse student body.  
  - **Continuous Monitoring:** Regular reviews of these key performance indicators can help identify early warning signs and enable timely adjustments in policies and practices.
  
- **Long-Term Planning:**  
  The insights from this dashboard support proactive decision-making, allowing the institution to address current challenges and forecast future trends in student engagement and success.
""")
st.markdown("""
This comprehensive dashboard is designed to empower administrators with actionable insights to continually improve admissions processes, student retention, and overall satisfaction.
""")
