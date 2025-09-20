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
API = st.sidebar.text_input('Backend API URL', value='http://localhost:8003')

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
            st.plotly_chart(fig, width='stretch')

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
            name = st.text_input("Candidate Name*")
            email = st.text_input("Email Address*")
            uploaded_file = st.file_uploader(
                "Resume File*",
                type=["pdf", "docx"],
                help="Upload PDF or DOCX format only"
            )
            
            submit = st.form_submit_button("🚀 Upload & Parse Resume")
            
            if submit and name and email and uploaded_file:
                with st.spinner("Uploading and analyzing resume..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    data = {"name": name, "email": email}
                    
                    result = post_api_data("/api/resumes", data=data, files=files)
                    
                    if result:
                        st.success("✅ Resume uploaded and analyzed successfully!")
                        
                        # Show parsing results
                        if 'parsed_info' in result:
                            parsed = result['parsed_info']
                            st.subheader("🔍 Parsing Results")
                            
                            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                            with metrics_col1:
                                st.metric("Skills Found", parsed['skills_found'])
                            with metrics_col2:
                                st.metric("Education", parsed['education_entries'])
                            with metrics_col3:
                                st.metric("Experience", parsed['experience_entries'])
                            with metrics_col4:
                                st.metric("Projects", parsed['projects_found'])
    
    with col2:
        st.subheader("📋 Recent Uploads")
        resumes = get_api_data("/api/resumes", {"limit": 10})
        
        if resumes:
            for resume in resumes:
                st.write(f"**{resume['candidate_name']}**")
                st.write(f"Email: {resume['candidate_email']}")
                st.write(f"Uploaded: {resume['uploaded_at'][:10]}")
                st.write("---")

elif page == "Bulk Evaluation":
    st.header("🚀 Bulk Evaluation & Results")
    
    # Job selection for bulk evaluation
    jobs = get_api_data("/api/jobs")
    if jobs:
        selected_job = st.selectbox(
            "Select Job for Bulk Evaluation",
            options=[(job['id'], job['title']) for job in jobs],
            format_func=lambda x: f"{x[1]} (ID: {x[0]})"
        )
        
        if selected_job and st.button("🚀 Run Bulk Evaluation"):
            with st.spinner("Processing all resumes for this job..."):
                result = post_api_data("/api/bulk-evaluate", {"job_id": selected_job[0]})
                
                if result:
                    st.success(f"Processed {result['processed_count']} resumes!")
                    
                    # Show results summary
                    if 'results' in result:
                        results_df = pd.DataFrame(result['results'])
                        
                        if not results_df.empty and 'score' in results_df.columns:
                            # Score distribution
                            fig = px.histogram(results_df, x='score', nbins=10, 
                                             title="Score Distribution for Bulk Evaluation")
                            st.plotly_chart(fig, width='stretch')
                            
                            # Verdict summary
                            verdict_counts = results_df['verdict'].value_counts()
                            fig_pie = px.pie(values=verdict_counts.values, names=verdict_counts.index,
                                           title="Verdict Distribution")
                            st.plotly_chart(fig_pie, width='stretch')
    
    # Show evaluation results with filtering
    st.subheader("📉 Evaluation Results")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        verdict_filter = st.selectbox("Filter by Verdict", ["All", "High", "Medium", "Low"])
    with col2:
        if jobs:
            job_filter = st.selectbox(
                "Filter by Job",
                ["All"] + [(job['id'], job['title']) for job in jobs],
                format_func=lambda x: "All" if x == "All" else f"{x[1]}"
            )
    with col3:
        min_score = st.slider("Minimum Score", 0, 100, 0)
    
    # Fetch filtered evaluations
    params = {"limit": 100}
    if verdict_filter != "All":
        params["verdict"] = verdict_filter
    if job_filter != "All" and isinstance(job_filter, tuple):
        params["job_id"] = job_filter[0]
    
    evaluations = get_api_data("/api/evaluations", params)
    
    if evaluations:
        # Filter by minimum score
        filtered_evals = [ev for ev in evaluations if ev['final_score'] >= min_score]
        
        if filtered_evals:
            df = pd.DataFrame(filtered_evals)
            
            # Display results table
            st.dataframe(
                df[['candidate_name', 'job_title', 'final_score', 'verdict', 'eval_time']],
                width='stretch'
            )
            
            # Export functionality
            if st.button("📎 Export Results to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No evaluations found matching your criteria.")

elif page == "Analytics":
    st.header("📈 Analytics & Insights")
    
    evaluations = get_api_data("/api/evaluations", {"limit": 1000})
    
    if evaluations and len(evaluations) > 0:
        df = pd.DataFrame(evaluations)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution by verdict
            fig = px.box(df, x='verdict', y='final_score', 
                        title="Score Distribution by Verdict")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top missing skills
            all_missing = []
            for ev in evaluations:
                all_missing.extend(ev.get('missing_skills', []))
            
            if all_missing:
                from collections import Counter
                missing_counts = Counter(all_missing).most_common(10)
                
                fig = px.bar(
                    x=[count for skill, count in missing_counts],
                    y=[skill for skill, count in missing_counts],
                    orientation='h',
                    title="Top 10 Missing Skills",
                    labels={'x': 'Frequency', 'y': 'Skills'}
                )
                st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Evaluations over time
            df['eval_time'] = pd.to_datetime(df['eval_time'])
            daily_evals = df.groupby(df['eval_time'].dt.date).size()
            
            fig = px.line(x=daily_evals.index, y=daily_evals.values,
                         title="Evaluations Over Time",
                         labels={'x': 'Date', 'y': 'Number of Evaluations'})
            st.plotly_chart(fig, width='stretch')
            
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Total Evaluations", len(evaluations))
                st.metric("Average Score", f"{df['final_score'].mean():.1f}%")
            
            with col_b:
                st.metric("High Suitability", len(df[df['verdict'] == 'High']))
                st.metric("Median Score", f"{df['final_score'].median():.1f}%")
    else:
        st.info("No evaluation data available for analytics. Upload resumes and run evaluations first.")

# Footer
st.markdown("---")
st.markdown("🎆 **Innomatics Research Labs** - Resume Relevance Check System | Powered by AI")
