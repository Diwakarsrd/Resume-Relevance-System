#!/usr/bin/env python3
"""
Test script for the Enhanced Resume Relevance Check System
This script demonstrates the key features and capabilities.
"""

import requests
import time
import json
from pathlib import Path

API_BASE = "http://localhost:8003"

def test_api_connection():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        print("✅ API connection successful!")
        return True
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        print("Please make sure the FastAPI server is running with: uvicorn app.main:app --reload")
        return False

def create_sample_job():
    """Create a sample job posting"""
    job_data = {
        "title": "Senior Python Developer",
        "jd_text": """
        We are looking for a Senior Python Developer to join our AI/ML team.
        
        Responsibilities:
        - Develop scalable web applications using Python and FastAPI
        - Design and implement machine learning models
        - Work with databases (PostgreSQL, MongoDB)
        - Deploy applications using Docker and AWS
        - Collaborate with cross-functional teams
        
        Required Skills:
        - 3+ years of Python development experience
        - Experience with FastAPI, Django, or Flask
        - Knowledge of machine learning libraries (scikit-learn, pandas, numpy)
        - Database experience (SQL, NoSQL)
        - Git version control
        
        Preferred Skills:
        - AWS cloud services
        - Docker containerization
        - React.js for frontend development
        - Data visualization tools (Plotly, Matplotlib)
        
        Education: Bachelor's degree in Computer Science or related field
        """,
        "must_have": "python, fastapi, machine learning, sql, git",
        "nice_to_have": "aws, docker, react, plotly"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/jobs", data=job_data)
        result = response.json()
        print(f"✅ Job created successfully! ID: {result['job_id']}")
        
        if 'parsed_info' in result:
            parsed = result['parsed_info']
            print("🤖 AI-parsed job information:")
            print(f"  - Must-have skills: {parsed.get('must_have_skills', [])}")
            print(f"  - Nice-to-have skills: {parsed.get('nice_to_have_skills', [])}")
            print(f"  - Required education: {parsed.get('required_education', [])}")
        
        return result['job_id']
    except Exception as e:
        print(f"❌ Failed to create job: {e}")
        return None

def create_sample_resume():
    """Create a sample resume text file for testing"""
    resume_content = """
John Smith
Software Developer
Email: john.smith@email.com
Phone: (555) 123-4567

EDUCATION
Bachelor of Technology in Computer Science
XYZ University, 2020

SKILLS
Programming Languages: Python, JavaScript, Java
Web Frameworks: FastAPI, Django, React.js
Machine Learning: scikit-learn, pandas, numpy, matplotlib
Databases: PostgreSQL, MongoDB, MySQL
Tools: Git, Docker, VS Code
Cloud: Basic AWS knowledge

EXPERIENCE
Software Developer | Tech Company (2021-2023)
- Developed web applications using Python and FastAPI
- Built REST APIs serving 10,000+ daily requests
- Worked with PostgreSQL databases for data storage
- Collaborated with team using Git version control

Junior Developer | Startup Inc. (2020-2021)
- Created data analysis scripts using Python and pandas
- Built interactive dashboards with plotly
- Learned machine learning basics with scikit-learn

PROJECTS
E-commerce API (2023)
- Built a complete e-commerce backend using FastAPI
- Integrated with PostgreSQL database
- Implemented user authentication and payment processing
- Technologies: Python, FastAPI, PostgreSQL, Docker

Data Analysis Dashboard (2022)
- Created interactive data visualization dashboard
- Used pandas for data processing and plotly for visualization
- Analyzed sales data to identify trends
- Technologies: Python, pandas, plotly, streamlit

Machine Learning Model (2021)
- Built a customer churn prediction model
- Used scikit-learn for model development
- Achieved 85% accuracy on test dataset
- Technologies: Python, scikit-learn, pandas, numpy

CERTIFICATIONS
- Python Institute PCAP Certification (2022)
- AWS Cloud Practitioner (2023)
"""
    
    # Write to a temporary file
    resume_file = Path("sample_resume.txt")
    resume_file.write_text(resume_content)
    return resume_file

def upload_sample_resume():
    """Upload sample resume"""
    resume_file = create_sample_resume()
    
    try:
        with open(resume_file, 'rb') as f:
            files = {"file": ("sample_resume.txt", f, "text/plain")}
            data = {
                "name": "John Smith",
                "email": "john.smith@email.com"
            }
            
            response = requests.post(f"{API_BASE}/api/resumes", data=data, files=files)
            result = response.json()
            
            print(f"✅ Resume uploaded successfully! ID: {result['resume_id']}")
            
            if 'parsed_info' in result:
                parsed = result['parsed_info']
                print("📄 Resume parsing results:")
                print(f"  - Skills found: {parsed['skills_found']}")
                print(f"  - Education entries: {parsed['education_entries']}")
                print(f"  - Experience entries: {parsed['experience_entries']}")
                print(f"  - Projects found: {parsed['projects_found']}")
                print(f"  - Certifications found: {parsed['certifications_found']}")
            
            return result['resume_id']
    
    except Exception as e:
        print(f"❌ Failed to upload resume: {e}")
        return None
    finally:
        # Clean up
        if resume_file.exists():
            resume_file.unlink()

def evaluate_resume(job_id, resume_id):
    """Evaluate resume against job"""
    try:
        data = {"job_id": job_id, "resume_id": resume_id}
        response = requests.post(f"{API_BASE}/api/evaluate", data=data)
        result = response.json()
        
        print(f"✅ Evaluation completed! ID: {result['evaluation_id']}")
        print(f"📊 Results:")
        print(f"  - Final Score: {result['final_score']}/100")
        print(f"  - Verdict: {result['verdict']}")
        
        if 'detailed_scores' in result:
            detailed = result['detailed_scores']
            print(f"  - Must-have skills: {detailed['must_have_skills']}%")
            print(f"  - Nice-to-have skills: {detailed['nice_to_have_skills']}%")
            print(f"  - Education match: {detailed['education']}%")
            print(f"  - Experience match: {detailed['experience']}%")
            print(f"  - Project relevance: {detailed['projects']}%")
        
        print(f"\n💡 Feedback:")
        print(result.get('feedback', 'No feedback available'))
        
        print(f"\n🔍 Analysis:")
        print(f"  - Matched skills: {result.get('matched_skills', [])}")
        print(f"  - Missing skills: {result.get('missing_skills', [])}")
        
        return result['evaluation_id']
        
    except Exception as e:
        print(f"❌ Failed to evaluate resume: {e}")
        return None

def test_bulk_evaluation(job_id):
    """Test bulk evaluation functionality"""
    try:
        data = {"job_id": job_id}
        response = requests.post(f"{API_BASE}/api/bulk-evaluate", data=data)
        result = response.json()
        
        print(f"✅ Bulk evaluation completed!")
        print(f"📊 Results:")
        print(f"  - Processed: {result['processed_count']} resumes")
        
        if 'results' in result:
            for res in result['results'][:5]:  # Show first 5 results
                if 'score' in res:
                    print(f"  - Resume {res['resume_id']}: {res['score']}% ({res['verdict']})")
                else:
                    print(f"  - Resume {res['resume_id']}: Error - {res.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to run bulk evaluation: {e}")
        return False

def test_dashboard_apis():
    """Test dashboard API endpoints"""
    print("\n🔍 Testing Dashboard APIs:")
    
    # Test jobs listing
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        jobs = response.json()
        print(f"✅ Jobs API: Found {len(jobs)} jobs")
    except Exception as e:
        print(f"❌ Jobs API failed: {e}")
    
    # Test resumes listing
    try:
        response = requests.get(f"{API_BASE}/api/resumes")
        resumes = response.json()
        print(f"✅ Resumes API: Found {len(resumes)} resumes")
    except Exception as e:
        print(f"❌ Resumes API failed: {e}")
    
    # Test evaluations listing
    try:
        response = requests.get(f"{API_BASE}/api/evaluations")
        evaluations = response.json()
        print(f"✅ Evaluations API: Found {len(evaluations)} evaluations")
        
        # Test filtering
        if evaluations:
            response = requests.get(f"{API_BASE}/api/evaluations", params={"verdict": "High"})
            high_evals = response.json()
            print(f"✅ High verdict filter: Found {len(high_evals)} high-scoring evaluations")
            
    except Exception as e:
        print(f"❌ Evaluations API failed: {e}")

def main():
    """Run the complete test suite"""
    print("🚀 Starting Enhanced Resume Relevance System Test")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        return
    
    print("\n📋 Step 1: Creating sample job...")
    job_id = create_sample_job()
    if not job_id:
        return
    
    print(f"\n📄 Step 2: Uploading sample resume...")
    resume_id = upload_sample_resume()
    if not resume_id:
        return
    
    print(f"\n⚖️ Step 3: Evaluating resume against job...")
    evaluation_id = evaluate_resume(job_id, resume_id)
    if not evaluation_id:
        return
    
    print(f"\n🔄 Step 4: Testing bulk evaluation...")
    test_bulk_evaluation(job_id)
    
    print(f"\n🖥️ Step 5: Testing dashboard APIs...")
    test_dashboard_apis()
    
    print("\n" + "=" * 60)
    print("🎉 Test completed successfully!")
    print("\n📊 Next steps:")
    print("1. Start the Streamlit dashboard: streamlit run app/streamlit_app.py")
    print("2. Open your browser to http://localhost:8501")
    print("3. Explore the enhanced dashboard features:")
    print("   - Job Management with AI parsing")
    print("   - Resume Upload with detailed parsing")
    print("   - Bulk Evaluation capabilities")
    print("   - Analytics and insights")
    print("   - Export functionality")

if __name__ == "__main__":
    main()