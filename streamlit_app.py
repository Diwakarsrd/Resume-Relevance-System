import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Relevance System",
    page_icon="📋",
    layout="wide"
)

# Initialize session state
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'resumes' not in st.session_state:
    st.session_state.resumes = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []

st.title("Resume Relevance Check System")
st.markdown("**AI-Powered Resume Evaluation Platform for Innomatics Research Labs**")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page:",
    ["Dashboard", "Job Management", "Resume Upload", "Evaluation", "Analytics"]
)

# Helper functions
def extract_skills(text, custom_skills=None):
    """Extract skills from text using keyword matching"""
    # Default skill list - can be expanded
    default_skills = [
        'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'machine learning', 'data science', 'tensorflow',
        'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django', 'fastapi',
        'html', 'css', 'git', 'linux', 'excel', 'powerbi', 'tableau', 'spark',
        'hadoop', 'kafka', 'rest api', 'graphql', 'microservices', 'devops',
        'ci/cd', 'jenkins', 'terraform', 'ansible', 'spring', 'boot'
    ]
    
    skills_to_check = custom_skills if custom_skills else default_skills
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_to_check:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def calculate_score(required_skills, candidate_skills):
    """Calculate match score between required and candidate skills"""
    if not required_skills:
        return 85
    
    required_set = set(skill.lower().strip() for skill in required_skills)
    candidate_set = set(skill.lower().strip() for skill in candidate_skills)
    
    matches = len(required_set & candidate_set)
    total_required = len(required_set)
    
    score = int((matches / total_required) * 100) if total_required > 0 else 85
    return min(max(score, 0), 100)

def get_verdict(score):
    """Get verdict based on score"""
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    else:
        return "Low"

def generate_feedback(score, verdict, matched_skills, missing_skills):
    """Generate detailed feedback"""
    feedback = f"Overall Score: {score}% ({verdict} suitability)\n\n"
    
    if matched_skills:
        feedback += f"Strengths:\n"
        for skill in matched_skills:
            feedback += f"• {skill}\n"
        feedback += "\n"
    
    if missing_skills:
        feedback += f"Areas for Improvement:\n"
        for skill in missing_skills:
            feedback += f"• {skill}\n"
        feedback += "\n"
    
    if score < 70:
        feedback += "Recommendations:\n"
        feedback += "• Focus on developing the missing skills\n"
        feedback += "• Consider relevant certifications or training\n"
        feedback += "• Build projects that demonstrate these skills\n"
    
    return feedback

# Page content
if page == "Dashboard":
    st.header("Dashboard Overview")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(st.session_state.jobs))
    with col2:
        st.metric("Total Resumes", len(st.session_state.resumes))
    with col3:
        st.metric("Total Evaluations", len(st.session_state.evaluations))
    with col4:
        if st.session_state.evaluations:
            avg_score = sum(e['score'] for e in st.session_state.evaluations) / len(st.session_state.evaluations)
            st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.metric("Average Score", "N/A")
    
    # Recent evaluations table
    if st.session_state.evaluations:
        st.subheader("Recent Evaluations")
        df = pd.DataFrame(st.session_state.evaluations)
        
        # Format the dataframe for better display
        display_df = df[['candidate_name', 'job_title', 'score', 'verdict']].copy()
        display_df.columns = ['Candidate', 'Job Title', 'Score (%)', 'Verdict']
        
        # Color code the verdicts
        def highlight_verdict(val):
            if val == 'High':
                return 'background-color: #d4edda'
            elif val == 'Medium':
                return 'background-color: #fff3cd'
            elif val == 'Low':
                return 'background-color: #f8d7da'
            return ''
        
        styled_df = display_df.style.applymap(highlight_verdict, subset=['Verdict'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No evaluations yet. Start by creating jobs and uploading resumes.")

elif page == "Job Management":
    st.header("Job Management")
    
    tab1, tab2 = st.tabs(["Create New Job", "Existing Jobs"])
    
    with tab1:
        st.subheader("Create New Job Posting")
        
        with st.form("job_form", clear_on_submit=True):
            # Job details
            job_title = st.text_input("Job Title*", placeholder="e.g., Senior Python Developer")
            
            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("Location", placeholder="e.g., Remote, New York")
            with col2:
                experience = st.selectbox("Required Experience", 
                                        ["Entry Level", "1-2 years", "3-5 years", "5+ years"])
            
            job_description = st.text_area("Job Description*", 
                                         height=150,
                                         placeholder="Enter detailed job description...")
            
            # Skills section
            st.markdown("**Required Skills**")
            required_skills = st.text_area("Required Skills (one per line or comma separated)*",
                                         placeholder="python\nmachine learning\nsql\naws")
            
            preferred_skills = st.text_area("Preferred Skills (one per line or comma separated)",
                                          placeholder="docker\nkubernetes\ntensorflow")
            
            submitted = st.form_submit_button("Create Job", type="primary")
            
            if submitted:
                if job_title and job_description and required_skills:
                    # Parse skills
                    req_skills = [s.strip() for s in re.split(r'[,\n]', required_skills) if s.strip()]
                    pref_skills = [s.strip() for s in re.split(r'[,\n]', preferred_skills) if s.strip()]
                    
                    # Create job object
                    job = {
                        "id": len(st.session_state.jobs) + 1,
                        "title": job_title,
                        "location": location,
                        "experience": experience,
                        "description": job_description,
                        "required_skills": req_skills,
                        "preferred_skills": pref_skills,
                        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    st.session_state.jobs.append(job)
                    st.success(f"Job '{job_title}' created successfully! (ID: {job['id']})")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab2:
        st.subheader("Existing Jobs")
        
        if st.session_state.jobs:
            for job in st.session_state.jobs:
                with st.expander(f"{job['title']} (ID: {job['id']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Location:** {job.get('location', 'Not specified')}")
                        st.write(f"**Experience:** {job.get('experience', 'Not specified')}")
                        st.write(f"**Required Skills:** {', '.join(job['required_skills'])}")
                        if job['preferred_skills']:
                            st.write(f"**Preferred Skills:** {', '.join(job['preferred_skills'])}")
                        st.write(f"**Created:** {job.get('created_date', 'Unknown')}")
                    
                    with col2:
                        if st.button("Bulk Evaluate", key=f"bulk_{job['id']}", type="secondary"):
                            if st.session_state.resumes:
                                processed = 0
                                for resume in st.session_state.resumes:
                                    # Check if already evaluated
                                    existing = any(e['job_id'] == job['id'] and e['resume_id'] == resume['id'] 
                                                 for e in st.session_state.evaluations)
                                    if not existing:
                                        # Perform evaluation
                                        resume_skills = extract_skills(resume['content'])
                                        all_job_skills = job['required_skills'] + job['preferred_skills']
                                        
                                        matched_skills = list(set(all_job_skills) & set(resume_skills))
                                        missing_skills = list(set(job['required_skills']) - set(resume_skills))
                                        
                                        score = calculate_score(job['required_skills'], resume_skills)
                                        verdict = get_verdict(score)
                                        feedback = generate_feedback(score, verdict, matched_skills, missing_skills)
                                        
                                        evaluation = {
                                            "id": len(st.session_state.evaluations) + 1,
                                            "job_id": job['id'],
                                            "resume_id": resume['id'],
                                            "job_title": job['title'],
                                            "candidate_name": resume['name'],
                                            "score": score,
                                            "verdict": verdict,
                                            "matched_skills": matched_skills,
                                            "missing_skills": missing_skills,
                                            "feedback": feedback,
                                            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                                        }
                                        
                                        st.session_state.evaluations.append(evaluation)
                                        processed += 1
                                
                                st.success(f"Bulk evaluation completed! Processed {processed} new resumes.")
                                st.rerun()
                            else:
                                st.warning("No resumes available for evaluation.")
                        
                        if st.button("Delete", key=f"delete_{job['id']}", type="secondary"):
                            st.session_state.jobs = [j for j in st.session_state.jobs if j['id'] != job['id']]
                            st.success("Job deleted successfully!")
                            st.rerun()
        else:
            st.info("No jobs created yet. Create your first job using the form above.")

elif page == "Resume Upload":
    st.header("Resume Upload & Management")
    
    tab1, tab2 = st.tabs(["Upload Resume", "Manage Resumes"])
    
    with tab1:
        st.subheader("Upload New Resume")
        
        with st.form("resume_form", clear_on_submit=True):
            # Candidate details
            col1, col2 = st.columns(2)
            with col1:
                candidate_name = st.text_input("Candidate Name*", placeholder="John Doe")
            with col2:
                candidate_email = st.text_input("Email*", placeholder="john.doe@email.com")
            
            # Resume upload options
            upload_method = st.radio("Choose upload method:", 
                                    ["Upload file", "Paste resume text"])
            
            resume_content = ""
            
            if upload_method == "Upload file":
                uploaded_file = st.file_uploader("Choose resume file", 
                                                type=['txt', 'pdf', 'docx'],
                                                help="Supported formats: TXT, PDF, DOCX")
                
                if uploaded_file is not None:
                    if uploaded_file.type == "text/plain":
                        resume_content = str(uploaded_file.read(), "utf-8")
                    else:
                        st.warning("PDF and DOCX parsing requires additional libraries. Please use TXT files or paste text directly.")
                        resume_content = f"File uploaded: {uploaded_file.name}"
            
            else:  # Paste text
                resume_content = st.text_area("Paste resume text*", 
                                            height=300,
                                            placeholder="Paste the complete resume text here...")
            
            submitted = st.form_submit_button("Upload Resume", type="primary")
            
            if submitted:
                if candidate_name and candidate_email and resume_content:
                    # Extract skills from resume
                    extracted_skills = extract_skills(resume_content)
                    
                    # Create resume object
                    resume = {
                        "id": len(st.session_state.resumes) + 1,
                        "name": candidate_name,
                        "email": candidate_email,
                        "content": resume_content,
                        "skills": extracted_skills,
                        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    st.session_state.resumes.append(resume)
                    st.success(f"Resume for {candidate_name} uploaded successfully! (ID: {resume['id']})")
                    
                    # Show extracted skills
                    if extracted_skills:
                        st.write(f"**Skills found:** {', '.join(extracted_skills)}")
                    else:
                        st.warning("No recognizable skills found in the resume.")
                    
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab2:
        st.subheader("Uploaded Resumes")
        
        if st.session_state.resumes:
            for resume in st.session_state.resumes:
                with st.expander(f"{resume['name']} (ID: {resume['id']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Email:** {resume['email']}")
                        st.write(f"**Upload Date:** {resume['upload_date']}")
                        st.write(f"**Skills Found:** {', '.join(resume['skills'])}")
                        
                        # Show preview of resume content
                        preview = resume['content'][:200] + "..." if len(resume['content']) > 200 else resume['content']
                        st.text_area("Resume Preview:", preview, height=100, disabled=True)
                    
                    with col2:
                        if st.button("Delete", key=f"delete_resume_{resume['id']}", type="secondary"):
                            st.session_state.resumes = [r for r in st.session_state.resumes if r['id'] != resume['id']]
                            st.success("Resume deleted successfully!")
                            st.rerun()
        else:
            st.info("No resumes uploaded yet. Upload your first resume using the form above.")

elif page == "Evaluation":
    st.header("Resume Evaluation")
    
    if st.session_state.jobs and st.session_state.resumes:
        # Evaluation form
        with st.form("evaluation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Job selection
                job_options = {f"{job['title']} (ID: {job['id']})": job for job in st.session_state.jobs}
                selected_job_key = st.selectbox("Select Job Position:", list(job_options.keys()))
                selected_job = job_options[selected_job_key]
                
                # Show job details
                st.write(f"**Required Skills:** {', '.join(selected_job['required_skills'])}")
                if selected_job['preferred_skills']:
                    st.write(f"**Preferred Skills:** {', '.join(selected_job['preferred_skills'])}")
            
            with col2:
                # Resume selection
                resume_options = {f"{resume['name']} (ID: {resume['id']})": resume for resume in st.session_state.resumes}
                selected_resume_key = st.selectbox("Select Candidate:", list(resume_options.keys()))
                selected_resume = resume_options[selected_resume_key]
                
                # Show candidate skills
                st.write(f"**Candidate Skills:** {', '.join(selected_resume['skills'])}")
            
            submitted = st.form_submit_button("Evaluate Match", type="primary")
            
            if submitted:
                # Perform evaluation
                job_skills = selected_job['required_skills'] + selected_job['preferred_skills']
                resume_skills = selected_resume['skills']
                
                matched_skills = list(set(job_skills) & set(resume_skills))
                missing_required = list(set(selected_job['required_skills']) - set(resume_skills))
                missing_preferred = list(set(selected_job['preferred_skills']) - set(resume_skills))
                
                score = calculate_score(selected_job['required_skills'], resume_skills)
                verdict = get_verdict(score)
                feedback = generate_feedback(score, verdict, matched_skills, missing_required)
                
                # Save evaluation
                evaluation = {
                    "id": len(st.session_state.evaluations) + 1,
                    "job_id": selected_job['id'],
                    "resume_id": selected_resume['id'],
                    "job_title": selected_job['title'],
                    "candidate_name": selected_resume['name'],
                    "score": score,
                    "verdict": verdict,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_required,
                    "feedback": feedback,
                    "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                st.session_state.evaluations.append(evaluation)
                
                # Display results
                st.success("Evaluation completed successfully!")
                
                # Results section
                st.subheader("Evaluation Results")
                
                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Score", f"{score}%")
                with col2:
                    color = "normal"
                    if verdict == "High":
                        color = "normal"
                    elif verdict == "Medium":
                        color = "normal"
                    else:
                        color = "inverse"
                    st.metric("Verdict", verdict)
                with col3:
                    st.metric("Skills Matched", f"{len(matched_skills)}/{len(job_skills)}")
                
                # Detailed breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Matched Skills")
                    if matched_skills:
                        for skill in matched_skills:
                            st.success(f"✓ {skill}")
                    else:
                        st.info("No skills matched")
                
                with col2:
                    st.subheader("Missing Skills")
                    if missing_required:
                        st.write("**Required (Missing):**")
                        for skill in missing_required:
                            st.error(f"✗ {skill}")
                    
                    if missing_preferred:
                        st.write("**Preferred (Missing):**")
                        for skill in missing_preferred:
                            st.warning(f"◦ {skill}")
                    
                    if not missing_required and not missing_preferred:
                        st.info("All skills matched!")
                
                # Detailed feedback
                st.subheader("Detailed Feedback")
                st.text_area("Evaluation Feedback:", feedback, height=200, disabled=True)
    
    else:
        st.warning("Please create at least one job and upload at least one resume before performing evaluations.")
        
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.jobs:
                st.info("No jobs available. Go to 'Job Management' to create jobs.")
        with col2:
            if not st.session_state.resumes:
                st.info("No resumes available. Go to 'Resume Upload' to upload resumes.")

elif page == "Analytics":
    st.header("Analytics & Reports")
    
    if st.session_state.evaluations:
        # Create analytics dataframe
        df = pd.DataFrame(st.session_state.evaluations)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Evaluations", len(df))
        with col2:
            avg_score = df['score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}%")
        with col3:
            high_count = len(df[df['verdict'] == 'High'])
            st.metric("High Matches", high_count)
        with col4:
            low_count = len(df[df['verdict'] == 'Low'])
            st.metric("Low Matches", low_count)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Score Distribution")
            score_ranges = pd.cut(df['score'], bins=[0, 40, 60, 80, 100], labels=['0-40%', '41-60%', '61-80%', '81-100%'])
            score_counts = score_ranges.value_counts()
            st.bar_chart(score_counts)
        
        with col2:
            st.subheader("Verdict Distribution")
            verdict_counts = df['verdict'].value_counts()
            st.bar_chart(verdict_counts)
        
        # Job-wise analysis
        if len(df['job_title'].unique()) > 1:
            st.subheader("Performance by Job Position")
            job_stats = df.groupby('job_title')['score'].agg(['mean', 'count']).round(1)
            job_stats.columns = ['Average Score', 'Number of Evaluations']
            st.dataframe(job_stats, use_container_width=True)
        
        # Detailed evaluation history
        st.subheader("Evaluation History")
        display_df = df[['evaluation_date', 'candidate_name', 'job_title', 'score', 'verdict']].copy()
        display_df.columns = ['Date', 'Candidate', 'Job', 'Score (%)', 'Verdict']
        display_df = display_df.sort_values('Date', ascending=False)
        
        # Add color coding
        def highlight_verdict(val):
            if val == 'High':
                return 'background-color: #d4edda'
            elif val == 'Medium':
                return 'background-color: #fff3cd'
            elif val == 'Low':
                return 'background-color: #f8d7da'
            return ''
        
        styled_df = display_df.style.applymap(highlight_verdict, subset=['Verdict'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export functionality
        st.subheader("Export Data")
        if st.button("Download Evaluation Report (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("No evaluation data available yet. Perform some evaluations to see analytics.")

# Sidebar information
with st.sidebar:
    st.markdown("---")
    st.subheader("System Information")
    st.write(f"Jobs: {len(st.session_state.jobs)}")
    st.write(f"Resumes: {len(st.session_state.resumes)}")
    st.write(f"Evaluations: {len(st.session_state.evaluations)}")
    
    st.markdown("---")
    st.subheader("Data Management")
    
    if st.button("Clear All Data", type="secondary"):
        if st.session_state.get('confirm_clear', False):
            st.session_state.jobs = []
            st.session_state.resumes = []
            st.session_state.evaluations = []
            st.session_state.confirm_clear = False
            st.success("All data cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("Click again to confirm deletion of all data")
    
    # Reset confirmation if user navigates away
    if st.session_state.get('confirm_clear', False) and page:
        if st.session_state.get('last_page') != page:
            st.session_state.confirm_clear = False
        st.session_state.last_page = page

# Footer
st.markdown("---")
st.markdown("**Resume Relevance Check System** | Built for Innomatics Research Labs")