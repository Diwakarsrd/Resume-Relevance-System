import streamlit as st
import requests
import pandas as pd
import json
import threading
import time
import uvicorn

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Relevance System",
    page_icon="💼",
    layout="wide"
)

# In-memory storage for demo
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'resumes' not in st.session_state:
    st.session_state.resumes = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []

st.title("💼 Resume Relevance Check System")
st.markdown("### AI-Powered Resume Evaluation Platform")

# Navigation
page = st.sidebar.selectbox(
    "Navigate:",
    ["Dashboard", "Job Management", "Resume Upload", "Evaluation"]
)

def extract_skills(text):
    """Simple skill extraction"""
    skills = ['python', 'javascript', 'java', 'react', 'sql', 'docker', 'aws', 'machine learning', 'data science']
    found = []
    text_lower = text.lower()
    for skill in skills:
        if skill in text_lower:
            found.append(skill)
    return found

def calculate_score(job_skills, resume_skills):
    """Calculate match score"""
    if not job_skills:
        return 80
    matches = len(set(job_skills) & set(resume_skills))
    return int((matches / len(job_skills)) * 100)

if page == "Dashboard":
    st.header("📈 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jobs", len(st.session_state.jobs))
    with col2:
        st.metric("Resumes", len(st.session_state.resumes))
    with col3:
        st.metric("Evaluations", len(st.session_state.evaluations))
    with col4:
        if st.session_state.evaluations:
            avg_score = sum(e['score'] for e in st.session_state.evaluations) / len(st.session_state.evaluations)
            st.metric("Avg Score", f"{avg_score:.1f}%")
        else:
            st.metric("Avg Score", "N/A")
    
    if st.session_state.evaluations:
        st.subheader("🔄 Recent Evaluations")
        df = pd.DataFrame(st.session_state.evaluations)
        st.dataframe(df, use_container_width=True)

elif page == "Job Management":
    st.header("💼 Job Management")
    
    tab1, tab2 = st.tabs(["Create Job", "Existing Jobs"])
    
    with tab1:
        st.subheader("➕ Create New Job")
        
        with st.form("job_form"):
            title = st.text_input("Job Title*")
            jd = st.text_area("Job Description*", height=150)
            must_have = st.text_area("Must-Have Skills (comma separated)")
            
            if st.form_submit_button("🚀 Create Job"):
                if title and jd:
                    skills = [s.strip().lower() for s in must_have.split(",") if s.strip()]
                    job = {
                        "id": len(st.session_state.jobs) + 1,
                        "title": title,
                        "description": jd,
                        "skills": skills
                    }
                    st.session_state.jobs.append(job)
                    st.success(f"✅ Job created! ID: {job['id']}")
                    st.rerun()
                else:
                    st.error("Please fill in required fields")
    
    with tab2:
        st.subheader("📋 Existing Jobs")
        for job in st.session_state.jobs:
            with st.expander(f"{job['title']} (ID: {job['id']})"):
                st.write(f"**Skills:** {', '.join(job['skills'])}")
                if st.button(f"Bulk Evaluate", key=f"bulk_{job['id']}"):
                    processed = 0
                    for resume in st.session_state.resumes:
                        # Check if already evaluated
                        existing = any(e['job_id'] == job['id'] and e['resume_id'] == resume['id'] 
                                     for e in st.session_state.evaluations)
                        if not existing:
                            resume_skills = extract_skills(resume['text'])
                            score = calculate_score(job['skills'], resume_skills)
                            verdict = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
                            
                            evaluation = {
                                "job_id": job['id'],
                                "resume_id": resume['id'],
                                "job_title": job['title'],
                                "candidate_name": resume['name'],
                                "score": score,
                                "verdict": verdict
                            }
                            st.session_state.evaluations.append(evaluation)
                            processed += 1
                    
                    st.success(f"Processed {processed} resumes")
                    st.rerun()

elif page == "Resume Upload":
    st.header("📄 Resume Upload")
    
    with st.form("resume_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Candidate Name*")
        with col2:
            email = st.text_input("Email*")
        
        uploaded_file = st.file_uploader("Resume File (TXT)*", type=['txt'])
        
        if st.form_submit_button("📤 Upload Resume"):
            if name and email and uploaded_file:
                # Read file content
                text = uploaded_file.read().decode('utf-8', errors='ignore')
                skills = extract_skills(text)
                
                resume = {
                    "id": len(st.session_state.resumes) + 1,
                    "name": name,
                    "email": email,
                    "text": text,
                    "skills": skills
                }
                st.session_state.resumes.append(resume)
                st.success(f"✅ Resume uploaded! ID: {resume['id']}")
                st.write(f"**Skills found:** {', '.join(skills)}")
                st.rerun()
            else:
                st.error("Please fill all fields and upload a TXT file")

elif page == "Evaluation":
    st.header("🔍 Resume Evaluation")
    
    if st.session_state.jobs and st.session_state.resumes:
        with st.form("evaluate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_options = {f"{j['title']} (ID: {j['id']})": j for j in st.session_state.jobs}
                selected_job_name = st.selectbox("Select Job:", list(job_options.keys()))
            
            with col2:
                resume_options = {f"{r['name']} (ID: {r['id']})": r for r in st.session_state.resumes}
                selected_resume_name = st.selectbox("Select Resume:", list(resume_options.keys()))
            
            if st.form_submit_button("🎯 Evaluate"):
                if selected_job_name and selected_resume_name:
                    job = job_options[selected_job_name]
                    resume = resume_options[selected_resume_name]
                    
                    resume_skills = extract_skills(resume['text'])
                    job_skills = job['skills']
                    
                    matched_skills = list(set(job_skills) & set(resume_skills))
                    missing_skills = list(set(job_skills) - set(resume_skills))
                    
                    score = calculate_score(job_skills, resume_skills)
                    verdict = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
                    
                    st.success("✅ Evaluation Complete!")
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Score", f"{score}%")
                    with col2:
                        st.metric("Verdict", verdict)
                    with col3:
                        st.metric("Matched Skills", len(matched_skills))
                    
                    # Skills breakdown
                    if matched_skills:
                        st.subheader("✅ Matched Skills")
                        st.write(", ".join(matched_skills))
                    
                    if missing_skills:
                        st.subheader("❌ Missing Skills")
                        st.write(", ".join(missing_skills))
                    
                    # Save evaluation
                    evaluation = {
                        "job_id": job['id'],
                        "resume_id": resume['id'],
                        "job_title": job['title'],
                        "candidate_name": resume['name'],
                        "score": score,
                        "verdict": verdict
                    }
                    st.session_state.evaluations.append(evaluation)
    else:
        st.info("Please create jobs and upload resumes first.")

# Footer
st.markdown("---")
st.markdown("💼 **Resume Relevance System** | Streamlit Cloud Demo")

# Debug info in sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("**📊 Debug Info**")
    st.write(f"Jobs: {len(st.session_state.jobs)}")
    st.write(f"Resumes: {len(st.session_state.resumes)}")
    st.write(f"Evaluations: {len(st.session_state.evaluations)}")
    
    if st.button("🗑️ Clear All Data"):
        st.session_state.jobs = []
        st.session_state.resumes = []
        st.session_state.evaluations = []
        st.rerun()