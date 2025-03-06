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
# --- Interactive Key Findings & Actionable Insights ---
with st.expander("Click here to view Key Findings & Actionable Insights for Admissions Funnel Efficiency"):
    st.markdown("""
    **Admissions Funnel Efficiency:**
    
    - **Finding:**
      - The dashboard indicates a total of **59,400 applications**, **35,100 admissions**, and **13,980 enrollments**.
      - This corresponds to a conversion rate of approximately **59%** from applications to admissions, but only around **40%** of admitted students actually enroll.
    
    - **Actionable Insights:**
      - **Enhanced Follow-Up:** Deploy personalized communication strategies—such as targeted emails, campus visits, or webinars—to encourage admitted students to convert to enrolled.
      - **Financial Incentives:** Reevaluate and potentially expand scholarship and financial aid offerings to improve the enrollment yield.
      - **Targeted Recruitment:** Analyze demographic and geographic data to identify segments with lower conversion rates, then tailor recruitment strategies to address those gaps.
    """)

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
with st.expander("Click here to view Key Findings & Actionable Insights for Retention Rate Trends"):
    st.markdown("""
    **Retention Rate Trends:**
    
    - **Finding:**
      - The average retention rate across terms is approximately **87.10%**, indicating a generally healthy performance.
      - However, there are noticeable fluctuations in retention rates across different terms, with some periods experiencing dips that may signal challenges in student engagement or academic support.
    
    - **Actionable Insights:**
      - **Early Intervention Programs:** Introduce early warning systems and proactive academic advising during terms with lower retention to identify and support at-risk students.
      - **Enhanced Support Services:** Boost tutoring, mentoring, and counseling services during challenging periods to help improve student retention.
      - **Curriculum Review:** Analyze terms with significant retention dips to determine if curriculum changes or course delivery methods might be contributing factors, and consider appropriate adjustments.
    """)

# --- Student Satisfaction Trends ---
st.subheader("Student Satisfaction Trends")
fig_satisfaction = px.line(df, x="Year", y="Student Satisfaction (%)", markers=True,
                           title="Student Satisfaction over the years")
fig_satisfaction.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_satisfaction, use_container_width=True)
with st.expander("Click here to view Key Findings & Actionable Insights for Student Satisfaction Trends"):
    st.markdown("""
    **Student Satisfaction Trends:**
    
    - **Finding:**
      - The average student satisfaction score is approximately **82.60%**, suggesting that students generally have a positive experience.
      - However, there are fluctuations in satisfaction over the years, indicating that certain terms may have faced challenges in areas such as course delivery, support services, or campus facilities.
    
    - **Actionable Insights:**
      - **Deep-Dive Feedback:** Conduct detailed surveys or focus groups during periods of lower satisfaction to pinpoint specific areas that need improvement.
      - **Enhance Support Services:** Consider bolstering student support services and campus facilities to address concerns raised in feedback.
      - **Continuous Improvement:** Establish a transparent feedback loop where student input is regularly reviewed and leads to visible changes, thereby boosting overall satisfaction.
    """)

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
with st.expander("Click here to view Key Findings & Actionable Insights for Enrollment Breakdown by Department"):
    st.markdown("""
    **Enrollment Breakdown by Department:**
    
    - **Finding:**
      - The pie chart shows that the **Arts** department leads with approximately **35.5%** of total enrollments.
      - **Science** follows with around **26.4%**, **Engineering** with **21%**, and **Business** with **17.2%**.
      - This disparity indicates that certain departments are significantly more attractive or better marketed compared to others.
    
    - **Actionable Insights:**
      - **Targeted Recruitment:** Increase outreach and tailored marketing efforts for departments with lower enrollment (e.g., Business) to boost their appeal.
      - **Program Enhancement:** Review and potentially update the curriculum or program offerings in under-enrolled departments to align more closely with student interests and industry demands.
      - **Resource Allocation:** Consider adjusting resource distribution, such as faculty and facilities, to support growth in departments that are lagging behind.
      - **Stakeholder Engagement:** Engage with current students, alumni, and industry partners to gain insights into what makes certain departments more popular and use this information to improve the offerings in less popular areas.
    """)

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
with st.expander("Click here to view Key Findings & Actionable Insights for Seasonal Variations – Spring vs. Fall"):
    st.markdown("""
    **Seasonal Variations – Spring vs. Fall:**
    
    - **Finding:**
      - The data shows that **Fall terms consistently have higher enrollment numbers** compared to Spring.
      - This seasonal difference may be due to traditional application cycles, student preferences, or differences in program offerings between the two terms.
    
    - **Actionable Insights:**
      - **Resource Allocation:** Allocate more resources, such as faculty and support services, during Fall terms to manage the higher demand.
      - **Spring Recruitment Strategies:** Develop targeted marketing and recruitment initiatives for Spring terms, such as early admission incentives, flexible course schedules, or tailored program offerings.
      - **Trend Monitoring:** Continuously monitor seasonal enrollment trends to quickly adapt strategies and address any emerging discrepancies.
      - **Program Diversification:** Consider expanding or diversifying programs during the Spring term to increase its appeal and boost enrollment numbers.
    """)

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
with st.expander("Click here to view Key Findings & Actionable Insights for Departmental Trends Over Time"):
    st.markdown("""
    **Departmental Trends Over Time:**
    
    - **Finding:**
      - The grouped bar chart reveals that enrollment trends vary across different departments over multiple terms.
      - Some departments, such as Arts and Science, display consistent or growing trends, while others like Engineering and Business may show stagnation or declines in specific terms.
      - These variations suggest shifting student interests and possibly different levels of resource allocation or program appeal.
    
    - **Actionable Insights:**
      - **Data-Driven Strategy:** Use these trend insights to plan for future growth by investing in departments showing upward trends and re-evaluating programs in those with declining performance.
      - **Targeted Interventions:** For departments experiencing downturns, consider initiatives such as curriculum updates, enhanced marketing campaigns, or new industry partnerships to revitalize interest.
      - **Resource Optimization:** Adjust faculty and resource allocation based on long-term trends to support departments that are expanding.
      - **Stakeholder Engagement:** Collaborate with faculty, students, and industry experts to identify and address factors influencing these trends, ensuring that program offerings remain relevant and competitive.
    """)


