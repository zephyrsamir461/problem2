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
st.markdown(f"**Average Student Satisfaction (%):** {avg_satisfaction:.2f}%")

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
      - The number of applications, admissions and enrollments each term per year is same according to the bar chart.  
    
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
      - Retention rates have risen from around 85% in 2016 to approximately 90% by 2024, indicating steady progress over the observed period.
      - However, there are noticeable fluctuations in retention rates across different terms, with some periods experiencing dips around 2019–2020 (falling back near 85%) that may signal challenges in student engagement or academic support.
      - The retention rate climbs sharply from 2021 onward, suggesting that recent measures (e.g., improved student support or revised academic policies) have effectively helped more students persist in their studies.
    - **Actionable Insights:**
      - **Investigate Past Challenges:** Examine the conditions or policy changes around 2019–2020 to understand what caused the temporary drop in retention. Insights here can help prevent similar declines in the future.Introduce early warning systems and proactive academic advising during terms with lower retention to identify and support at-risk students.
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
      - Student satisfaction rose from around 78% in the mid-2010s to about 88% by 2024, reflecting a notable improvement in the overall student experience.  
      - The chart shows a steady upward trend with minor fluctuations—there’s a small dip around 2020, suggesting that specific events (e.g., changes in campus operations, global factors) may have temporarily impacted satisfaction levels.
      - From 2021 onward, the satisfaction rate climbs more sharply, indicating that recent initiatives (academic improvements, campus upgrades, or support services) have positively influenced student sentiment.
    - **Actionable Insights:**
      - **Investigate Factors Behind the Dip:** Analyze the context around the 2020 dip to determine any disruptions—such as pandemic-related transitions, shifts in course delivery, or campus closures—and develop strategies to mitigate similar impacts in the future. 
      - **Enhance Support Services:** Consider bolstering student support services and campus facilities to address concerns raised in feedback.Identify the most successful interventions implemented after 2021—such as expanded mental health support, improved online learning resources, or enhanced student engagement activities—and maintain or scale them.
      - **Continuous Improvement:** Establish a transparent feedback loop where student input is regularly reviewed and leads to visible changes, thereby boosting overall satisfaction.Demonstrating a strong trajectory of improvement can help attract prospective students.
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
      - The pie chart shows that the **Engineering** department leads with approximately **35.5%** of total enrollments.
      - **Business** follows with around **26.4%**, **Arts** with **21%**, and **Science** with **17.2%**.
      - This disparity indicates that certain departments are significantly more attractive or better marketed compared to others.
    
    - **Actionable Insights:**
      - **Targeted Recruitment:** Increase outreach and tailored marketing efforts for departments with lower enrollment (e.g., Science) to boost their appeal.
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
      - The data shows that both **Fall and **Spring terms consistently have the same enrollment numbers**.
      
    - **Actionable Insights:**
      - **Resource Allocation:** Allocate more resources, such as faculty and support services, during both terms to manage the higher demand.
      - **Term Recruitment Strategies:** Develop targeted marketing and recruitment initiatives for both terms, such as early admission incentives, flexible course schedules, or tailored program offerings.
      - **Trend Monitoring:** Continuously monitor seasonal enrollment trends to quickly adapt strategies and address any emerging discrepancies.
      - **Program Diversification:** Consider expanding or diversifying programs during both terms to increase its appeal and boost enrollment numbers.
    """)

# --- Compare Trends Between Departments ---
st.subheader("Departmental Enrollment Trends Over Terms")

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
    title="Departmental Enrollment Trends Over Terms"
)
fig_dept_trends.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_dept_trends, use_container_width=True)
with st.expander("Click here to view Key Findings & Actionable Insights for Departmental Trends Over Terms"):
    st.markdown("""
    **Departmental Trends Over Time:**
    
    - **Finding:**
      - Enrollment patterns remain consistent between Spring and Fall, meaning students are not showing a strong preference for one term over the other in terms of department choices.
      - Some departments, such as Engineering and Business, display consistent or growing trends, while others like Arts and Science may show stagnation or declines in specific terms.
      - These variations suggest shifting student interests and possibly different levels of resource allocation or program appeal.
    
    - **Actionable Insights:**
      - **Data-Driven Strategy:** Use these trend insights to plan for future growth by investing in departments showing upward trends and re-evaluating programs in those with declining performance.
      - **Targeted Interventions:** For departments experiencing downturns, consider initiatives such as curriculum updates, enhanced marketing campaigns, or new industry partnerships to revitalize interest.
      - **Resource Optimization:** Adjust faculty and resource allocation based on long-term trends to support departments that are expanding.
      - **Stakeholder Engagement:** Collaborate with faculty, students, and industry experts to identify and address factors influencing these trends, ensuring that program offerings remain relevant and competitive.
    """)

# --- Compare Departmental Enrollment Trends Over Multiple Years ---
st.subheader("Departmental Enrollment Trends Over Multiple Years")

# Convert department enrollment data into long format for trend analysis
df_dept_trends = df.melt(
    id_vars=["Year"],
    value_vars=["Arts Enrolled", "Science Enrolled", "Engineering Enrolled", "Business Enrolled"],
    var_name="Department",
    value_name="Enrollments"
)

# Create a line chart showing department enrollment trends over years
fig_dept_trend_years = px.line(
    df_dept_trends,
    x="Year",
    y="Enrollments",
    color="Department",
    markers=True,
    title="Departmental Enrollment Trends Over Years"
)
fig_dept_trend_years.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_dept_trend_years, use_container_width=True)

# --- Interactive Key Findings & Actionable Insights ---
with st.expander("Click here to view Key Findings & Actionable Insights on Student Trends Over Years"):
    st.markdown("""
**Trends in Departmental Enrollment Over the Years:**

- **Finding:**
-**Engineering Enrollment Shows Consistent Growth:** Engineering has experienced steady growth, rising from just above 200 enrollments in 2015 to nearly 300 by 2024.This suggests strong demand and sustained student interest in the field.
-**Business Enrollment is Growing but at a Slower Rate:** Business enrollment has been increasing but at a slower pace compared to Engineering.While it started near 150 enrollments in 2015, the growth trajectory suggests moderate but stable interest.
-**Arts Enrollment is Gradually Increasing:** The Arts department has shown steady but slower growth. The increase is noticeable, though it remains behind Engineering and Business in overall numbers.
-**Science Enrollment is Declining:**Unlike other departments, Science enrollments initially remained stable but started to decline from 2019 onward.By 2024, Science enrollment is at its lowest in the observed period, suggesting a potential drop in interest or external factors affecting student decisions.

- **Actionable Insights:**
- **Expand Engineering Programs to Sustain Growth:** Given consistent demand, consider increasing faculty, lab resources, and industry partnerships to support future growth. Develop specialized tracks (e.g., AI, Robotics, Renewable Energy) to attract an even broader student base.
- **Enhance Business Offerings to Strengthen Growth:** While growing slowly, Business could benefit from more specialized programs such as Finance, Entrepreneurship, or Tech-Driven Business. Strengthen industry collaboration by offering internship-based programs and networking events.
- **Support Science Programs to Reverse the Decline:** Investigate why enrollments are decreasing—this could be due to limited job prospects, outdated course structures, or competitive programs elsewhere. Consider modernizing the curriculum, introducing interdisciplinary programs (e.g., Data Science, Environmental Science), and enhancing lab/research opportunities.
- **Continue Arts Program Promotion & Diversification:** Arts enrollment is increasing but remains below Engineering and Business.Consider launching cross-disciplinary programs that integrate Arts with Business or Technology (e.g., Digital Media, UX/UI Design, or Film & Entrepreneurship).Strengthen career-focused initiatives (e.g., internships, industry projects) to showcase real-world applications of an Arts degree.""")
