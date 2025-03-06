import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="University Dashboard", layout="wide")

st.title("University Dashboard")

# --- Data Loading & Preparation ---
@st.cache_data
def load_data():
    df = pd.read_csv("university_student_dashboard_data.csv")
    # Expected columns include: "Term", "Applications", "Admitted", "Enrolled",
    # "Retention Rate (%)", "Student Satisfaction (%)", "Arts Enrolled", "Science Enrolled",
    # "Engineering Enrolled", "Business Enrolled"
    df['Season'] = df['Term'].apply(lambda x: 'Spring' if 'Spring' in x else ('Fall' if 'Fall' in x else 'Other'))
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Only Term filter is needed since department info comes from individual columns
term_options = ['All'] + sorted(df['Term'].unique().tolist())
selected_term = st.sidebar.selectbox("Select Term", term_options)

# Apply term filter
filtered_df = df.copy()
if selected_term != "All":
    filtered_df = filtered_df[filtered_df["Term"] == selected_term]

# --- Summary KPIs ---
total_applications = filtered_df["Applications"].sum()
total_admissions = filtered_df["Admitted"].sum()
# Use the "Enrollments" column if available; otherwise compute from departmental columns
total_enrollments = filtered_df["Enrolled"].sum() if "Enrolled" in filtered_df.columns else (
    filtered_df["Arts Enrolled"].sum() +
    filtered_df["Science Enrolled"].sum() +
    filtered_df["Engineering Enrolled"].sum() +
    filtered_df["Business Enrolled"].sum()
)
avg_retention = filtered_df["Retention Rate (%)"].mean()
avg_satisfaction = filtered_df["Student Satisfaction (%)"].mean()

st.subheader("Summary Metrics")
st.markdown(f"**Total Applications:** {total_applications:,}")
st.markdown(f"**Total Admitted:** {total_admissions:,}")
st.markdown(f"**Total Enrolled:** {total_enrollments:,}")
st.markdown(f"**Average Retention Rate (%):** {avg_retention:.2f}%")
st.markdown(f"**Average Student Satisfaction (%):** {avg_satisfaction:.2f}")

# --- Admissions Overview Panel ---
st.subheader("Admissions Overview")
admissions_data = filtered_df.groupby("Term").agg({
    "Applications": "sum",
    "Admitted": "sum",
    "Enrolled": "sum"
}).reset_index()

fig_admissions = px.bar(admissions_data, x="Term", y=["Applications", "Admitted", "Enrolled"],
                        barmode="group", title="Applications, Admissions, and Enrollments per Term")
fig_admissions.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_admissions, use_container_width=True)

# --- Retention Rate Trends ---
st.subheader("Retention Rate Trends")
fig = px.scatter(
    df, 
    x="Year", 
    y="Retention Rate (%)", 
    title="Retention Rate Trends Over Time",
    labels={"Retention_Rate": "Retention Rate (%)"}
)
# Connect data points with lines (this assumes the data is ordered by term)
fig.update_traces(mode='lines+markers')
fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)
# --- Student Satisfaction Trends ---
st.subheader("Student Satisfaction Trends")
fig_satisfaction = px.line(df, x="Year", y="Student Satisfaction (%)", markers=True,
                           title="Student Satisfaction over the years")
fig_satisfaction.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_satisfaction, use_container_width=True)

# --- Enrollment Breakdown by Department ---
st.subheader("Enrollment Breakdown by Department")
# Create a DataFrame for the four departments using their respective enrollment columns
dept_data = pd.DataFrame({
    "Department": ["Arts", "Science", "Engineering", "Business"],
    "Enrollments": [
        filtered_df["Arts Enrolled"].sum(),
        filtered_df["Science Enrolled"].sum(),
        filtered_df["Engineering Enrolled"].sum(),
        filtered_df["Business Enrolled"].sum()
    ]
})
fig_enrollment_dept = px.pie(dept_data, names="Department", values="Enrollments",
                             title="Enrollment Breakdown by Department")
st.plotly_chart(fig_enrollment_dept, use_container_width=True)

# --- Spring vs Fall Term Comparison ---
st.subheader("Spring vs Fall Term Comparison")
spring_data = filtered_df[filtered_df["Season"] == "Spring"].groupby("Term").agg({
    "Applications": "sum",
    "Admitted": "sum",
    "Enrolled": "sum",
    "Retention Rate (%)": "mean",
    "Student Satisfaction (%)": "mean"
}).reset_index()

fall_data = filtered_df[filtered_df["Season"] == "Fall"].groupby("Term").agg({
    "Applications": "sum",
    "Admitted": "sum",
    "Enrolled": "sum",
    "Retention Rate (%)": "mean",
    "Student Satisfaction (%)": "mean"
}).reset_index()

if not spring_data.empty:
    spring_data["Season"] = "Spring"
if not fall_data.empty:
    fall_data["Season"] = "Fall"

if not spring_data.empty or not fall_data.empty:
    combined = pd.concat([spring_data, fall_data])
    fig_spring_fall = px.bar(combined, x="Term", y="Enrolled", color="Season",
                             barmode="group", title="Enrollments Comparison: Spring vs Fall")
    fig_spring_fall.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_spring_fall, use_container_width=True)
else:
    st.write("Insufficient data for Spring vs Fall comparison.")

# --- Compare Trends Between Departments ---
st.subheader("Departmental Enrollment Trends Over Time")

# Define the enrollment columns for each department
dept_columns = ["Arts Enrolled", "Science Enrolled", "Engineering Enrolled", "Business Enrolled"]

# Convert the wide-format departmental columns into a long-format DataFrame
df_dept_long = filtered_df.melt(
    id_vars=["Term", "Year"],
    value_vars=dept_columns,
    var_name="Department",
    value_name="Enrollments"
)

# Create a line chart comparing trends between departments
fig_dept_trends = px.bar(
    df_dept_long,
    x="Term",
    y="Enrollments",
    color="Department",
    barmode="group",
    title="Departmental Enrollment Trends Over Time"
)
fig_dept_trends.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_dept_trends, use_container_width=True)
# --- Key Findings & Actionable Insights ---
st.subheader("Key Findings & Actionable Insights")

st.markdown("""
**1. Admissions Funnel Efficiency:**
- **Finding:** Out of 59,400 total applications, 35,100 were admitted (roughly a 59% admission rate), and only 13,980 students enrolled. This suggests that while initial interest is strong, the conversion from admission to enrollment is around 40%.
- **Actionable Insight:** Focus on enrollment yield strategies such as targeted follow-ups, improved scholarship offers, and enhanced campus visit programs to boost conversion rates.

**2. Retention Rate Trends:**
- **Finding:** The average retention rate is 87.10%, which is healthy compared to industry standards. However, the retention trend shows some fluctuations across terms.
- **Actionable Insight:** Analyze terms with lower retention rates to identify potential issues (e.g., curriculum challenges or student support gaps) and consider interventions like academic advising, mentoring programs, or early alert systems.

**3. Student Satisfaction Trends:**
- **Finding:** Student satisfaction averages 82.60%. Although this indicates a generally positive experience, there are variations over time that warrant attention.
- **Actionable Insight:** Conduct deeper surveys or focus groups in terms or years with lower satisfaction scores to pinpoint concerns. Use this feedback to improve aspects such as course delivery, support services, and campus amenities.

**4. Enrollment Breakdown by Department:**
- **Finding:** The enrollment distribution shows that Arts leads with 35.5%, followed by Science (26.4%), Engineering (21%), and Business (17.2%). This significant disparity may reflect differences in program appeal or recruitment effectiveness.
- **Actionable Insight:** Consider targeted marketing and program enhancements for departments with lower enrollment (e.g., Business) while leveraging the strong performance of the Arts department to develop interdisciplinary programs.

**5. Seasonal Variations – Spring vs. Fall:**
- **Finding:** The comparison between Spring and Fall terms clearly indicates that Fall enrollment is substantially higher than Spring. This seasonal pattern may be due to traditional application cycles or student preferences.
- **Actionable Insight:** Adjust resource allocation and scheduling to manage higher demand in Fall. Additionally, develop strategies (such as early admission incentives or targeted outreach) to improve Spring term enrollment.

**6. Departmental Trends Over Time:**
- **Finding:** The grouped bar chart comparing departmental enrollment trends over time shows variations that may indicate shifting student interests or market demands.
- **Actionable Insight:** Monitor these trends longitudinally to inform decisions on resource planning, curriculum development, and program investments. For departments experiencing a downward trend, consider revising program offerings or increasing promotional efforts.
""")

