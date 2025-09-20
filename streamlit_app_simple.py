import streamlit as st
import requests
import pandas as pd
import json
import threading
import time
import uvicorn
from pathlib import Path
import sys
import os

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
if str(app_dir) not in sys.path:
    sys.path.append(str(app_dir))

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Relevance System",
    page_icon="💼",
    layout="wide"
)

# Simplified FastAPI backend starter
@st.cache_resource
def start_fastapi_server():
    """Start a minimal FastAPI server"""
    try:
        # Import the main FastAPI app
        from main import app as fastapi_app
        
        def run_server():
            uvicorn.run(
                fastapi_app, 
                host="0.0.0.0", 
                port=8080, 
                log_level="error"
            )
        
        # Start FastAPI in background thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(5)  # Give server time to start
        
        return "✅ FastAPI backend started"
    except Exception as e:
        return f"❌ Backend error: {str(e)}"

# Start backend
server_status = start_fastapi_server()

# API Configuration
API_BASE = "http://localhost:8080"
API = st.sidebar.text_input('Backend API URL', value=API_BASE)

st.title("💼 Resume Relevance Check System")
st.markdown("### AI-Powered Resume Evaluation Platform")

# Show server status
with st.sidebar:
    st.markdown("**🔧 Backend Status**")
    if "✅" in server_status:
        st.success(server_status)
    else:
        st.error(server_status)

# Navigation
page = st.sidebar.selectbox(
    "Navigate:",
    ["Dashboard", "Job Management", "Resume Upload", "Evaluation"]
)

def api_request(method, endpoint, data=None, files=None):
    """Make API request with error handling"""
    try:
        url = f"{API}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, params=data or {}, timeout=10)
        else:
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            else:
                response = requests.post(url, data=data or {}, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend not ready. Please wait...")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

if page == "Dashboard":
    st.header("📈 Dashboard")
    
    # Test API connection
    health = api_request("GET", "/health")
    if not health:
        st.warning("⏳ Waiting for backend to start...")
        if st.button("🔄 Retry"):
            st.rerun()
        st.stop()
    
    # Get data
    jobs = api_request("GET", "/api/jobs", {"limit": 100}) or []
    resumes = api_request("GET", "/api/resumes", {"limit": 100}) or []
    evaluations = api_request("GET", "/api/evaluations", {"limit": 100}) or []
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jobs", len(jobs))
    with col2:
        st.metric("Resumes", len(resumes))
    with col3:
        st.metric("Evaluations", len(evaluations))
    with col4:
        if evaluations:
            avg_score = sum(e['final_score'] for e in evaluations) / len(evaluations)
            st.metric("Avg Score", f"{avg_score:.1f}%")
        else:
            st.metric("Avg Score", "N/A")
    
    # Recent evaluations
    if evaluations:
        st.subheader("🔄 Recent Evaluations")
        df = pd.DataFrame(evaluations[:10])
        st.dataframe(df[['candidate_name', 'job_title', 'final_score', 'verdict']], use_container_width=True)

elif page == "Job Management":
    st.header("💼 Job Management")
    
    tab1, tab2 = st.tabs(["Create Job", "Existing Jobs"])
    
    with tab1:
        st.subheader("➕ Create New Job")
        
        with st.form("job_form"):
            title = st.text_input("Job Title*")
            jd = st.text_area("Job Description*", height=150)
            must_have = st.text_area("Must-Have Skills (comma separated)")
            nice_to_have = st.text_area("Nice-to-Have Skills (comma separated)")
            
            if st.form_submit_button("🚀 Create Job"):
                if title and jd:
                    with st.spinner("Creating job..."):
                        result = api_request("POST", "/api/jobs", {
                            "title": title,
                            "jd_text": jd,
                            "must_have": must_have,
                            "nice_to_have": nice_to_have
                        })
                        
                        if result:
                            st.success(f"✅ Job created! ID: {result['job_id']}")
                            if 'parsed_info' in result:
                                st.json(result['parsed_info'])
                else:
                    st.error("Please fill in required fields")
    
    with tab2:
        st.subheader("📋 Existing Jobs")
        jobs = api_request("GET", "/api/jobs", {"limit": 20})
        
        if jobs:
            for job in jobs:
                with st.expander(f"{job['title']} (ID: {job['id']})"):
                    st.write(f"**Skills:** {', '.join(job.get('must_have', []))}")
                    if st.button(f"Bulk Evaluate", key=f"bulk_{job['id']}"):
                        with st.spinner("Running bulk evaluation..."):
                            result = api_request("POST", "/api/bulk-evaluate", {"job_id": job['id']})
                            if result:
                                st.success(f"Processed {result['processed_count']} resumes")

elif page == "Resume Upload":
    st.header("📄 Resume Upload")
    
    with st.form("resume_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Candidate Name*")
        with col2:
            email = st.text_input("Email*")
        
        uploaded_file = st.file_uploader("Resume File (PDF/DOCX/TXT)*", type=['pdf', 'docx', 'txt'])
        
        if st.form_submit_button("📤 Upload Resume"):
            if name and email and uploaded_file:
                with st.spinner("Uploading and parsing..."):
                    files = {"file": uploaded_file}
                    data = {"name": name, "email": email}
                    result = api_request("POST", "/api/resumes", data, files)
                    
                    if result:
                        st.success(f"✅ Resume uploaded! ID: {result['resume_id']}")
                        if 'parsed_info' in result:
                            st.json(result['parsed_info'])
            else:
                st.error("Please fill all fields and upload a file")

elif page == "Evaluation":
    st.header("🔍 Resume Evaluation")
    
    # Get jobs and resumes
    jobs = api_request("GET", "/api/jobs") or []
    resumes = api_request("GET", "/api/resumes") or []
    
    if jobs and resumes:
        with st.form("evaluate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_options = {f"{j['title']} (ID: {j['id']})": j['id'] for j in jobs}
                selected_job = st.selectbox("Select Job:", list(job_options.keys()))
            
            with col2:
                resume_options = {f"{r['candidate_name']} (ID: {r['id']})": r['id'] for r in resumes}
                selected_resume = st.selectbox("Select Resume:", list(resume_options.keys()))
            
            if st.form_submit_button("🎯 Evaluate"):
                if selected_job and selected_resume:
                    job_id = job_options[selected_job]
                    resume_id = resume_options[selected_resume]
                    
                    with st.spinner("Evaluating..."):
                        result = api_request("POST", "/api/evaluate", {
                            "job_id": job_id,
                            "resume_id": resume_id
                        })
                        
                        if result:
                            st.success("✅ Evaluation Complete!")
                            
                            # Display results
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Score", f"{result['final_score']}%")
                            with col2:
                                st.metric("Verdict", result['verdict'])
                            with col3:
                                st.metric("Matched Skills", len(result.get('matched_skills', [])))
                            
                            # Skills breakdown
                            if result.get('matched_skills'):
                                st.subheader("✅ Matched Skills")
                                st.write(", ".join(result['matched_skills']))
                            
                            if result.get('missing_skills'):
                                st.subheader("❌ Missing Skills")
                                st.write(", ".join(result['missing_skills']))
                            
                            if result.get('feedback'):
                                st.subheader("💡 Feedback")
                                st.write(result['feedback'])
    else:
        st.info("Please create jobs and upload resumes first.")

# Footer
st.markdown("---")
st.markdown("💼 **Resume Relevance System** | Streamlit Cloud Deployment")