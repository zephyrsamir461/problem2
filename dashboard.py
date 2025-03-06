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
- **Finding:**
  - The dashboard shows a total of 59,400 applications, with 35,100 students admitted and 13,980 ultimately enrolled.
  - This indicates a conversion rate from application to admission of about 59%, but the yield from admitted to enrolled is only around 40%.
- **Actionable Insights:**
  - **Targeted Follow-Ups:** Enhance personalized communication with admitted students through phone calls, emails, or campus visits.
  - **Financial Incentives:** Reassess scholarship and financial aid offerings to boost enrollment among admitted students.
  - **Data Analysis:** Investigate demographic and geographic trends to identify segments with lower conversion rates and tailor recruitment strategies accordingly.

**2. Retention Rate Trends:**
- **Finding:**
  - The average retention rate across terms is 87.10%, suggesting that most enrolled students continue their studies.
  - However, some terms exhibit slight dips in retention, which might signal issues like academic challenges or insufficient student support.
- **Actionable Insights:**
  - **Early Intervention:** Implement early warning systems and academic advising for students in terms with lower retention.
  - **Enhanced Support Services:** Increase resources such as tutoring, mentoring programs, and counseling services during challenging terms.
  - **Program Review:** Examine course structures or curriculum changes that coincide with lower retention periods to identify potential improvements.

**3. Student Satisfaction Trends:**
- **Finding:**
  - Student satisfaction averages at 82.60%, with variations noted over different years.
  - Declines in satisfaction during certain periods could be linked to factors like course delivery quality, campus facilities, or student services.
- **Actionable Insights:**
  - **Deep-Dive Surveys:** Conduct detailed surveys or focus groups during low-satisfaction periods to identify specific areas for improvement.
  - **Faculty Development:** Enhance professional development programs for instructors to improve teaching effectiveness.
  - **Facility Upgrades:** Invest in campus facilities and support services to directly address areas where student feedback indicates room for improvement.
  - **Feedback Loop:** Establish a transparent process where student feedback is regularly reviewed and acted upon, with visible outcomes communicated back to the student body.

**4. Enrollment Breakdown by Department:**
- **Finding:**
  - Enrollment by department shows disparities: Arts (35.5%), Science (26.4%), Engineering (21%), and Business (17.2%).
  - The higher percentage in Arts might indicate strong interest or effective recruitment, while lower enrollments in Business and Engineering may suggest opportunities for growth.
- **Actionable Insights:**
  - **Department-Specific Marketing:** Increase marketing and outreach efforts for departments with lower enrollments, particularly Business and Engineering.
  - **Curriculum Innovation:** Review and modernize program offerings in underperforming departments to better align with market demands.
  - **Interdisciplinary Programs:** Consider creating interdisciplinary programs that combine strengths from higher-enrollment areas (like Arts) with those in lower-enrollment departments.
  - **Industry Partnerships:** Develop strategic partnerships with industry to enhance the appeal and employability of graduates from Business and Engineering.

**5. Seasonal Variations – Spring vs. Fall:**
- **Finding:**
  - The Spring vs. Fall comparison clearly indicates that Fall terms have significantly higher enrollment numbers compared to Spring.
  - This seasonal trend may reflect traditional application cycles or differences in student decision-making around the academic calendar.
- **Actionable Insights:**
  - **Resource Planning:** Allocate resources, faculty, and support services more heavily during Fall to manage higher enrollment.
  - **Spring Recruitment:** Develop targeted recruitment strategies for the Spring term, such as early admission incentives or flexible scheduling options.
  - **Flexible Start Dates:** Consider offering alternative or mini-term programs in Spring to attract a broader pool of students.
  - **Trend Monitoring:** Regularly review seasonal data to ensure that strategic adjustments remain aligned with evolving enrollment patterns.

**6. Departmental Trends Over Time:**
- **Finding:**
  - Analysis of departmental enrollment trends over time reveals variations that may indicate shifting student interests or changing market demands.
  - Some departments show growth while others remain static or decline, which can impact resource allocation and program planning.
- **Actionable Insights:**
  - **Longitudinal Analysis:** Continuously monitor and analyze departmental trends to identify long-term growth or decline patterns.
  - **Strategic Investment:** Invest in expanding programs within departments showing robust growth, including additional faculty hires and infrastructure improvements.
  - **Program Revitalization:** For departments with declining trends, consider curriculum updates, increased marketing efforts, or even merging programs to better meet student and industry needs.
  - **Stakeholder Engagement:** Engage with industry stakeholders, alumni, and current students to gather insights that can help reshape and modernize department offerings.
""")


