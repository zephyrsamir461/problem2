import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="University Dashboard", layout="wide")

st.title("University Dashboard: Admissions, Retention & Satisfaction")

# --- Data Loading & Preparation ---
@st.cache_data
def load_data():
    df = pd.read_csv("university_student_dashboard_data.csv")
    # Expected columns include: "Term", "Applications", "Admitted", "Enrolled",
    # "Retention Rate (%)", "Student Satisfaction (%)", "Arts Enrolled", "Science Enrolled",
    # "Engineering Enrolled", "Business Enrolled"
    df['Season'] = df['Term'].apply(lambda x: 'Spring' if 'Spring' in x else ('Fall' if 'Fall' in x else 'Other'))
    df['Year'] = df['Term'].str.extract(r'(\d{4})')
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
retention_data = filtered_df.groupby("Term")["Retention Rate (%)"].mean().reset_index()
fig_retention = px.line(retention_data, x="Term", y="Retention Rate (%)", markers=True,
                        title="Average Retention Rate per Term")
fig_retention.update_layout(xaxis_tickangle=-45, yaxis_title="Retention Rate (%)")
st.plotly_chart(fig_retention, use_container_width=True)

# --- Student Satisfaction Trends ---
st.subheader("Student Satisfaction Trends")
satisfaction_data = filtered_df.groupby("Term")["Student Satisfaction (%)"].mean().reset_index()
fig_satisfaction = px.line(satisfaction_data, x="Term", y="Student Satisfaction (%)", markers=True,
                           title="Average Student Satisfaction Score per Term")
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
