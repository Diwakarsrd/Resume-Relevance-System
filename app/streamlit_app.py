import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="Resume Relevance System",
    page_icon="💼",
    layout="wide"
)

# API Configuration
API = st.sidebar.text_input('Backend API URL', value='http://localhost:8080')

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 5px solid #1f77b4;
}
.high-score { border-left-color: #2ca02c !important; }
.medium-score { border-left-color: #ff7f0e !important; }
.low-score { border-left-color: #d62728 !important; }
</style>
""", unsafe_allow_html=True)

st.title("💼 Resume Relevance Check System")
st.markdown("### AI-Powered Resume Evaluation Platform for Innomatics Research Labs")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard Overview", "Job Management", "Resume Upload", "Bulk Evaluation", "Analytics"]
)

def get_api_data(endpoint, params=None):
    """Helper function to fetch data from API"""
    try:
        response = requests.get(f"{API}{endpoint}", params=params or {})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def post_api_data(endpoint, data=None, files=None):
    """Helper function to post data to API"""
    try:
        if files:
            response = requests.post(f"{API}{endpoint}", data=data, files=files)
        else:
            response = requests.post(f"{API}{endpoint}", data=data)
        return response.json()
    except Exception as e:
        st.error(f"Submission Error: {str(e)}")
        return None

if page == "Dashboard Overview":
    st.header("📈 Dashboard Overview")
    
    # Fetch overview data
    jobs = get_api_data("/api/jobs", {"limit": 100})
    resumes = get_api_data("/api/resumes", {"limit": 100})
    evaluations = get_api_data("/api/evaluations", {"limit": 100})
    
    if jobs and resumes and evaluations:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", len(jobs))
        with col2:
            st.metric("Total Resumes", len(resumes))
        with col3:
            st.metric("Total Evaluations", len(evaluations))
        with col4:
            if evaluations:
                avg_score = sum(ev['final_score'] for ev in evaluations) / len(evaluations)
                st.metric("Average Score", f"{avg_score:.1f}%")
        
        # Recent evaluations
        st.subheader("🔄 Recent Evaluations")
        if evaluations:
            df = pd.DataFrame(evaluations)
            df['eval_time'] = pd.to_datetime(df['eval_time'])
            df = df.sort_values('eval_time', ascending=False).head(10)
            
            # Color code by verdict
            def color_verdict(verdict):
                colors = {'High': 'background-color: #d4edda', 'Medium': 'background-color: #fff3cd', 'Low': 'background-color: #f8d7da'}
                return colors.get(verdict, '')
            
            styled_df = df[['candidate_name', 'job_title', 'final_score', 'verdict', 'eval_time']].style.map(
                lambda x: color_verdict(x) if x in ['High', 'Medium', 'Low'] else '', subset=['verdict']
            )
            st.dataframe(styled_df, use_container_width=True)
        
        # Score distribution chart
        if evaluations:
            st.subheader("📉 Score Distribution")
            scores = [ev['final_score'] for ev in evaluations]
            fig = px.histogram(x=scores, nbins=20, title="Distribution of Resume Scores")
            fig.update_layout(xaxis_title="Score", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Job Management":
    st.header("💼 Job Management")
    
    tab1, tab2 = st.tabs(["Create New Job", "Manage Existing Jobs"])
    
    with tab1:
        st.subheader("➕ Create New Job Posting")
        
        with st.form("job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Job Title*", placeholder="e.g., Senior Python Developer")
                must_have = st.text_area("Must-Have Skills (comma separated)", 
                                       placeholder="python, fastapi, sql, machine learning")
            
            with col2:
                nice_to_have = st.text_area("Nice-to-Have Skills (comma separated)", 
                                          placeholder="docker, kubernetes, aws")
                
            jd = st.text_area("Job Description*", height=200, 
                            placeholder="Enter the complete job description...")
            
            submit = st.form_submit_button("🚀 Create Job with AI Analysis")
            
            if submit and title and jd:
                with st.spinner("Creating job and analyzing requirements..."):
                    result = post_api_data("/api/jobs", {
                        "title": title,
                        "jd_text": jd,
                        "must_have": must_have,
                        "nice_to_have": nice_to_have
                    })
                    
                    if result:
                        st.success(f"✅ Job created successfully! ID: {result['job_id']}")
                        
                        if 'parsed_info' in result:
                            st.subheader("🤖 AI Analysis Results")
                            parsed = result['parsed_info']
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Detected Must-Have Skills:**")
                                for skill in parsed.get('must_have_skills', [])[:10]:
                                    st.write(f"• {skill}")
                            
                            with col2:
                                st.write("**Detected Nice-to-Have Skills:**")
                                for skill in parsed.get('nice_to_have_skills', [])[:10]:
                                    st.write(f"• {skill}")
    
    with tab2:
        st.subheader("📋 Existing Jobs")
        jobs = get_api_data("/api/jobs", {"limit": 50})
        
        if jobs:
            for job in jobs:
                with st.expander(f"{job['title']} (ID: {job['id']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Location:** {job.get('location', 'Not specified')}")
                        st.write(f"**Must-Have Skills:** {', '.join(job.get('must_have', []))}")
                    
                    with col2:
                        if st.button(f"Bulk Evaluate", key=f"bulk_{job['id']}"):
                            st.session_state[f"bulk_job_{job['id']}"] = True
                    
                    # Show bulk evaluation results if triggered
                    if st.session_state.get(f"bulk_job_{job['id']}", False):
                        with st.spinner("Running bulk evaluation..."):
                            bulk_result = post_api_data("/api/bulk-evaluate", {"job_id": job['id']})
                            if bulk_result:
                                st.success(f"Processed {bulk_result['processed_count']} resumes")
                                # Reset the state
                                st.session_state[f"bulk_job_{job['id']}"] = False

elif page == "Resume Upload":
    st.header("📄 Resume Upload & Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⬆️ Upload New Resume")
        
        with st.form("resume_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                name = st.text_input("Candidate Name*", placeholder="John Doe")
            with col_b:
                email = st.text_input("Email*", placeholder="john@example.com")
            
            uploaded_file = st.file_uploader(
                "Choose resume file (PDF/DOCX/TXT)*",
                type=['pdf', 'docx', 'txt'],
                help="Upload a resume in PDF, DOCX, or TXT format"
            )
            
            submit = st.form_submit_button("📤 Upload & Parse Resume")
            
            if submit and name and email and uploaded_file:
                with st.spinner("Uploading and parsing resume..."):
                    files = {"file": uploaded_file}
                    data = {"name": name, "email": email}
                    result = post_api_data("/api/resumes", data, files)
                    
                    if result:
                        st.success(f"✅ Resume uploaded successfully! ID: {result['resume_id']}")
                        
                        if 'parsed_info' in result:
                            st.subheader("📊 Parsing Results")
                            parsed = result['parsed_info']
                            
                            col_x, col_y, col_z = st.columns(3)
                            with col_x:
                                st.metric("Skills Found", parsed.get('skills_found', 0))
                            with col_y:
                                st.metric("Experience Entries", parsed.get('experience_entries', 0))
                            with col_z:
                                st.metric("Education Entries", parsed.get('education_entries', 0))
    
    with col2:
        st.subheader("📊 Upload Statistics")
        resumes = get_api_data("/api/resumes", {"limit": 100})
        if resumes:
            st.metric("Total Resumes", len(resumes))
            
            # Recent uploads
            st.write("**Recent Uploads:**")
            for resume in resumes[:5]:
                st.write(f"• {resume.get('candidate_name', 'Unknown')} - {resume.get('candidate_email', 'No email')}")

elif page == "Bulk Evaluation":
    st.header("🔍 Bulk Resume Evaluation")
    
    # Job selection for bulk evaluation
    jobs = get_api_data("/api/jobs", {"limit": 100})
    resumes = get_api_data("/api/resumes", {"limit": 100})
    
    if jobs and resumes:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Select Job for Bulk Evaluation")
            
            job_options = {f"{job['title']} (ID: {job['id']})": job['id'] for job in jobs}
            selected_job_name = st.selectbox("Choose Job:", list(job_options.keys()))
            
            if selected_job_name:
                job_id = job_options[selected_job_name]
                selected_job = next(job for job in jobs if job['id'] == job_id)
                
                st.write(f"**Must-Have Skills:** {', '.join(selected_job.get('must_have', []))}")
                st.write(f"**Nice-to-Have Skills:** {', '.join(selected_job.get('nice_to_have', []))}")
                
                if st.button("🚀 Start Bulk Evaluation", type="primary"):
                    with st.spinner(f"Evaluating all resumes against {selected_job['title']}..."):
                        result = post_api_data("/api/bulk-evaluate", {"job_id": job_id})
                        
                        if result:
                            st.success(f"✅ Bulk evaluation completed!")
                            st.info(f"📊 Processed {result['processed_count']} resumes")
                            
                            # Show some sample results
                            evaluations = get_api_data("/api/evaluations", {"job_id": job_id, "limit": 10})
                            if evaluations:
                                st.subheader("📈 Sample Results")
                                df = pd.DataFrame(evaluations)
                                st.dataframe(df[['candidate_name', 'final_score', 'verdict']], use_container_width=True)
        
        with col2:
            st.subheader("📊 Statistics")
            st.metric("Available Jobs", len(jobs))
            st.metric("Available Resumes", len(resumes))
            
            evaluations = get_api_data("/api/evaluations", {"limit": 100})
            if evaluations:
                st.metric("Total Evaluations", len(evaluations))

elif page == "Analytics":
    st.header("📊 Analytics & Insights")
    
    evaluations = get_api_data("/api/evaluations", {"limit": 200})
    jobs = get_api_data("/api/jobs", {"limit": 100})
    
    if evaluations and jobs:
        # Convert to DataFrame
        df = pd.DataFrame(evaluations)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Score Distribution by Verdict")
            verdict_counts = df['verdict'].value_counts()
            fig = px.pie(values=verdict_counts.values, names=verdict_counts.index, 
                        title="Evaluation Verdicts Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Average Scores by Job")
            job_scores = df.groupby('job_title')['final_score'].mean().sort_values(ascending=False)
            fig = px.bar(x=job_scores.values, y=job_scores.index, 
                        title="Average Resume Scores by Job Position", orientation='h')
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline analysis
        st.subheader("📅 Evaluation Timeline")
        df['eval_time'] = pd.to_datetime(df['eval_time'])
        daily_evals = df.groupby(df['eval_time'].dt.date).size()
        
        fig = px.line(x=daily_evals.index, y=daily_evals.values, 
                     title="Daily Evaluation Volume")
        fig.update_layout(xaxis_title="Date", yaxis_title="Evaluations")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.subheader("📋 Detailed Evaluation Results")
        st.dataframe(df.sort_values('eval_time', ascending=False), use_container_width=True)
    
    else:
        st.info("No evaluation data available yet. Start by creating jobs and uploading resumes!")

# Footer
st.markdown("---")
st.markdown("💼 **Resume Relevance Check System** | Powered by AI | Built for Innomatics Research Labs")