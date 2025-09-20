import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Resume Relevance System",
    page_icon="R",
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
    ["Dashboard", "Job Management", "Resume Upload", "Bulk Operations", "Evaluation", "Analytics", "AI Assistant"]
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
            feedback += f"+ {skill}\n"
        feedback += "\n"
    
    if missing_skills:
        feedback += f"Areas for Improvement:\n"
        for skill in missing_skills:
            feedback += f"- {skill}\n"
        feedback += "\n"
    
    if score < 70:
        feedback += "Recommendations:\n"
        feedback += "- Focus on developing the missing skills\n"
        feedback += "- Consider relevant certifications or training\n"
        feedback += "- Build projects that demonstrate these skills\n"
    
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

elif page == "Bulk Operations":
    st.header("Bulk Operations & Advanced Processing")
    
    tab1, tab2, tab3 = st.tabs(["Bulk Resume Upload", "Smart Matching", "Auto-Scoring"])
    
    with tab1:
        st.subheader("Bulk Resume Upload")
        st.markdown("Upload multiple resumes at once for efficient processing")
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "Upload Multiple Resume Files",
            type=['txt'],
            accept_multiple_files=True,
            help="Select multiple TXT files to upload at once"
        )
        
        # Bulk text input
        st.markdown("**OR paste multiple resumes (separated by '---')**")
        bulk_text = st.text_area(
            "Bulk Resume Text",
            height=200,
            placeholder="Resume 1 content here\n---\nResume 2 content here\n---\nResume 3 content here"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            auto_extract_names = st.checkbox("Auto-extract candidate names", value=True)
        with col2:
            auto_extract_emails = st.checkbox("Auto-extract emails", value=True)
        
        if st.button("Process Bulk Upload", type="primary"):
            processed_count = 0
            
            # Process uploaded files
            if uploaded_files:
                for i, uploaded_file in enumerate(uploaded_files):
                    try:
                        content = str(uploaded_file.read(), "utf-8")
                        
                        # Auto-extract name and email if enabled
                        name = f"Candidate_{len(st.session_state.resumes) + i + 1}"
                        email = f"candidate{len(st.session_state.resumes) + i + 1}@email.com"
                        
                        if auto_extract_names:
                            # Simple name extraction (first line or filename)
                            lines = content.strip().split('\n')
                            if lines and len(lines[0].split()) <= 4:
                                name = lines[0].strip()
                            else:
                                name = uploaded_file.name.split('.')[0].replace('_', ' ').title()
                        
                        if auto_extract_emails:
                            # Simple email extraction
                            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            emails = re.findall(email_pattern, content)
                            if emails:
                                email = emails[0]
                        
                        # Extract skills
                        skills = extract_skills(content)
                        
                        # Create resume object
                        resume = {
                            "id": len(st.session_state.resumes) + i + 1,
                            "name": name,
                            "email": email,
                            "content": content,
                            "skills": skills,
                            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "source": "bulk_upload"
                        }
                        
                        st.session_state.resumes.append(resume)
                        processed_count += 1
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            # Process bulk text
            if bulk_text.strip():
                resume_texts = [text.strip() for text in bulk_text.split('---') if text.strip()]
                
                for i, content in enumerate(resume_texts):
                    try:
                        # Auto-extract name and email
                        name = f"Candidate_{len(st.session_state.resumes) + i + 1}"
                        email = f"candidate{len(st.session_state.resumes) + i + 1}@email.com"
                        
                        if auto_extract_names:
                            lines = content.strip().split('\n')
                            if lines and len(lines[0].split()) <= 4:
                                name = lines[0].strip()
                        
                        if auto_extract_emails:
                            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                            emails = re.findall(email_pattern, content)
                            if emails:
                                email = emails[0]
                        
                        # Extract skills
                        skills = extract_skills(content)
                        
                        # Create resume object
                        resume = {
                            "id": len(st.session_state.resumes) + processed_count + i + 1,
                            "name": name,
                            "email": email,
                            "content": content,
                            "skills": skills,
                            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "source": "bulk_text"
                        }
                        
                        st.session_state.resumes.append(resume)
                        processed_count += 1
                        
                    except Exception as e:
                        st.error(f"Error processing resume {i+1}: {str(e)}")
            
            if processed_count > 0:
                st.success(f"Successfully processed {processed_count} resumes!")
                st.rerun()
            else:
                st.warning("No resumes to process. Please upload files or paste text.")
    
    with tab2:
        st.subheader("Smart Job-Resume Matching")
        st.markdown("AI-powered intelligent matching based on multiple criteria")
        
        if st.session_state.jobs and st.session_state.resumes:
            # Advanced matching options
            st.markdown("**Matching Criteria:**")
            col1, col2 = st.columns(2)
            
            with col1:
                skill_weight = st.slider("Skills Weight", 0.0, 1.0, 0.7, 0.1)
                min_score_threshold = st.slider("Minimum Score Threshold", 0, 100, 60, 5)
            
            with col2:
                top_matches = st.number_input("Top matches per job", min_value=1, max_value=10, value=3)
            
            # Smart matching algorithm
            if st.button("Run Smart Matching", type="primary"):
                matches_found = 0
                
                for job in st.session_state.jobs:
                    st.write(f"**Matching for: {job['title']}**")
                    
                    job_matches = []
                    
                    for resume in st.session_state.resumes:
                        # Calculate score
                        skill_score = calculate_score(job['required_skills'], resume['skills'])
                        
                        if skill_score >= min_score_threshold:
                            job_matches.append({
                                'resume': resume,
                                'score': skill_score,
                                'matched_skills': list(set(job['required_skills']) & set(resume['skills'])),
                                'missing_skills': list(set(job['required_skills']) - set(resume['skills']))
                            })
                    
                    # Sort by score
                    job_matches.sort(key=lambda x: x['score'], reverse=True)
                    
                    if job_matches:
                        st.write(f"Found {len(job_matches)} qualified candidates:")
                        
                        # Display top matches in a table
                        match_data = []
                        for match in job_matches[:top_matches]:
                            match_data.append({
                                'Candidate': match['resume']['name'],
                                'Score': f"{match['score']}%",
                                'Matched Skills': len(match['matched_skills']),
                                'Missing Skills': len(match['missing_skills']),
                                'Skills': ', '.join(match['matched_skills'][:3]) + ('...' if len(match['matched_skills']) > 3 else '')
                            })
                        
                        match_df = pd.DataFrame(match_data)
                        st.dataframe(match_df, use_container_width=True)
                        matches_found += len(job_matches)
                    else:
                        st.write("No qualified candidates found.")
                    
                    st.markdown("---")
                
                st.info(f"Smart matching completed! Found {matches_found} total matches.")
        else:
            st.warning("Please add jobs and resumes first.")
    
    with tab3:
        st.subheader("Automated Scoring & Ranking")
        st.markdown("Automatically score all resumes against all jobs")
        
        if st.session_state.jobs and st.session_state.resumes:
            # Auto-scoring options
            col1, col2 = st.columns(2)
            
            with col1:
                include_feedback = st.checkbox("Generate detailed feedback", value=True)
                save_results = st.checkbox("Save results to evaluations", value=True)
            
            with col2:
                top_n = st.number_input("Show top N candidates per job", min_value=1, max_value=10, value=3)
            
            if st.button("Run Auto-Scoring", type="primary"):
                scoring_results = []
                
                progress_bar = st.progress(0)
                total_combinations = len(st.session_state.jobs) * len(st.session_state.resumes)
                current_combination = 0
                
                for job in st.session_state.jobs:
                    job_results = []
                    
                    for resume in st.session_state.resumes:
                        current_combination += 1
                        progress_bar.progress(current_combination / total_combinations)
                        
                        # Calculate comprehensive score
                        score = calculate_score(job['required_skills'], resume['skills'])
                        verdict = get_verdict(score)
                        
                        matched_skills = list(set(job['required_skills']) & set(resume['skills']))
                        missing_skills = list(set(job['required_skills']) - set(resume['skills']))
                        
                        result = {
                            'job_title': job['title'],
                            'candidate_name': resume['name'],
                            'score': score,
                            'verdict': verdict,
                            'matched_skills': matched_skills,
                            'missing_skills': missing_skills
                        }
                        
                        if include_feedback:
                            result['feedback'] = generate_feedback(score, verdict, matched_skills, missing_skills)
                        
                        job_results.append(result)
                        
                        # Save to evaluations if requested
                        if save_results:
                            evaluation = {
                                "id": len(st.session_state.evaluations) + current_combination,
                                "job_id": job['id'],
                                "resume_id": resume['id'],
                                "job_title": job['title'],
                                "candidate_name": resume['name'],
                                "score": score,
                                "verdict": verdict,
                                "matched_skills": matched_skills,
                                "missing_skills": missing_skills,
                                "feedback": result.get('feedback', ''),
                                "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            
                            # Check if evaluation already exists
                            existing = any(
                                e['job_id'] == job['id'] and e['resume_id'] == resume['id']
                                for e in st.session_state.evaluations
                            )
                            
                            if not existing:
                                st.session_state.evaluations.append(evaluation)
                    
                    # Sort job results by score
                    job_results.sort(key=lambda x: x['score'], reverse=True)
                    scoring_results.append({
                        'job': job,
                        'results': job_results[:top_n]  # Top N candidates
                    })
                
                progress_bar.empty()
                
                # Display results
                st.subheader("Auto-Scoring Results")
                
                for job_result in scoring_results:
                    st.write(f"**{job_result['job']['title']}** - Top {len(job_result['results'])} Candidates:")
                    
                    if job_result['results']:
                        results_data = []
                        for result in job_result['results']:
                            results_data.append({
                                'Rank': len(results_data) + 1,
                                'Candidate': result['candidate_name'],
                                'Score': f"{result['score']}%",
                                'Verdict': result['verdict'],
                                'Matched Skills': len(result['matched_skills']),
                                'Missing Skills': len(result['missing_skills'])
                            })
                        
                        results_df = pd.DataFrame(results_data)
                        st.dataframe(results_df, use_container_width=True)
                    else:
                        st.write("No candidates found.")
                    
                    st.markdown("---")
                
                st.success(f"Auto-scoring completed for {len(st.session_state.jobs)} jobs and {len(st.session_state.resumes)} resumes!")
        else:
            st.warning("Please add jobs and resumes first.")    

elif page == "AI Assistant":
    st.header("AI-Powered Assistant")
    st.markdown("Get intelligent insights and recommendations")
    
    tab1, tab2 = st.tabs(["Resume Analysis", "Smart Recommendations"])
    
    with tab1:
        st.subheader("Advanced Resume Analysis")
        
        if st.session_state.resumes:
            selected_resume_id = st.selectbox(
                "Select Resume for Analysis",
                options=[r['id'] for r in st.session_state.resumes],
                format_func=lambda x: next(r['name'] for r in st.session_state.resumes if r['id'] == x)
            )
            
            selected_resume = next(r for r in st.session_state.resumes if r['id'] == selected_resume_id)
            
            if st.button("Analyze Resume", type="primary"):
                st.subheader("AI Analysis Results")
                
                # Skill analysis
                resume_skills = selected_resume['skills']
                all_job_skills = []
                for job in st.session_state.jobs:
                    all_job_skills.extend(job['required_skills'])
                
                skill_demand = {}
                for skill in set(all_job_skills):
                    skill_demand[skill] = all_job_skills.count(skill)
                
                # Calculate skill value
                valuable_skills = [skill for skill in resume_skills if skill in skill_demand]
                missing_valuable_skills = [skill for skill, demand in skill_demand.items() 
                                         if demand > 1 and skill not in resume_skills]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**High-Demand Skills Found:**")
                    for skill in valuable_skills:
                        demand_count = skill_demand.get(skill, 0)
                        st.success(f"{skill} (Demand: {demand_count} jobs)")
                    
                    if not valuable_skills:
                        st.info("No high-demand skills found")
                
                with col2:
                    st.markdown("**Recommended Skills to Learn:**")
                    for skill in sorted(missing_valuable_skills, 
                                      key=lambda x: skill_demand[x], reverse=True)[:5]:
                        demand_count = skill_demand[skill]
                        st.warning(f"{skill} (Demand: {demand_count} jobs)")
                    
                    if not missing_valuable_skills:
                        st.info("No additional skills recommended")
                
                # Resume strength analysis
                st.subheader("Resume Completeness Analysis")
                
                content = selected_resume['content'].lower()
                
                # Check for key sections
                sections_check = {
                    'Experience/Work History': any(word in content for word in ['experience', 'work', 'employment', 'position']),
                    'Education': any(word in content for word in ['education', 'degree', 'university', 'college']),
                    'Skills': any(word in content for word in ['skills', 'technical', 'proficient']),
                    'Projects': any(word in content for word in ['project', 'portfolio', 'github']),
                    'Certifications': any(word in content for word in ['certification', 'certified', 'license'])
                }
                
                strength_score = sum(sections_check.values()) / len(sections_check) * 100
                
                st.metric("Resume Completeness Score", f"{strength_score:.0f}%")
                
                for section, present in sections_check.items():
                    if present:
                        st.success(f"+ {section} section found")
                    else:
                        st.error(f"- {section} section missing")
        else:
            st.info("No resumes available for analysis")
    
    with tab2:
        st.subheader("Smart Recommendations")
        
        if st.session_state.jobs and st.session_state.resumes:
            # Generate intelligent recommendations
            if st.button("Generate Recommendations", type="primary"):
                st.subheader("AI-Powered Insights")
                
                # Market demand analysis
                all_required_skills = []
                for job in st.session_state.jobs:
                    all_required_skills.extend(job['required_skills'])
                
                skill_demand_count = {}
                for skill in set(all_required_skills):
                    skill_demand_count[skill] = all_required_skills.count(skill)
                
                # Supply analysis
                all_candidate_skills = []
                for resume in st.session_state.resumes:
                    all_candidate_skills.extend(resume['skills'])
                
                skill_supply_count = {}
                for skill in set(all_candidate_skills):
                    skill_supply_count[skill] = all_candidate_skills.count(skill)
                
                # Market gap analysis
                st.markdown("**Market Gap Analysis:**")
                
                high_demand_low_supply = []
                for skill, demand in skill_demand_count.items():
                    supply = skill_supply_count.get(skill, 0)
                    if demand >= 2 and supply < demand:
                        gap_ratio = demand / max(supply, 1)
                        high_demand_low_supply.append((skill, demand, supply, gap_ratio))
                
                high_demand_low_supply.sort(key=lambda x: x[3], reverse=True)
                
                if high_demand_low_supply:
                    st.markdown("**Skills in High Demand but Low Supply:**")
                    for skill, demand, supply, ratio in high_demand_low_supply[:5]:
                        st.error(f"{skill}: {demand} jobs need it, only {supply} candidates have it (Gap: {ratio:.1f}x)")
                    
                    st.markdown("**Recommendations:**")
                    st.info("- Consider training programs for high-gap skills")
                    st.info("- Recruit externally for these critical skills")
                    st.info("- Adjust job requirements to be more flexible")
                else:
                    st.success("Good supply-demand balance across all skills!")
                
                # Best matches summary
                st.markdown("**Top Performing Candidates:**")
                
                if st.session_state.evaluations:
                    eval_df = pd.DataFrame(st.session_state.evaluations)
                    top_performers = eval_df.nlargest(5, 'score')
                    
                    for _, performer in top_performers.iterrows():
                        st.success(f"{performer['candidate_name']}: {performer['score']}% for {performer['job_title']}")
                else:
                    st.info("Run evaluations to see top performers")
        else:
            st.info("Add jobs and resumes to get recommendations")

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
                            st.success(f"+ {skill}")
                    else:
                        st.info("No skills matched")
                
                with col2:
                    st.subheader("Missing Skills")
                    if missing_required:
                        st.write("**Required (Missing):**")
                        for skill in missing_required:
                            st.error(f"- {skill}")
                    
                    if missing_preferred:
                        st.write("**Preferred (Missing):**")
                        for skill in missing_preferred:
                            st.warning(f"~ {skill}")
                    
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