from rapidfuzz import fuzz
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import re
import os

# Initialize Gemini client
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
except ImportError:
    genai = None

def canon(s: str) -> str:
    """Canonicalize string for matching"""
    return s.lower().replace("-", " ").replace("_", " ").strip()

def advanced_skill_matching(required_skills: List[str], candidate_skills: List[str], threshold: int = 70) -> Tuple[List[str], List[str], int]:
    """Advanced skill matching with fuzzy matching and synonyms"""
    # Skill synonyms mapping
    skill_synonyms = {
        'javascript': ['js', 'node.js', 'nodejs', 'ecmascript'],
        'python': ['py', 'python3', 'python2'],
        'machine learning': ['ml', 'artificial intelligence', 'ai'],
        'database': ['db', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
        'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services'],
        'frontend': ['front-end', 'ui', 'user interface', 'react', 'angular', 'vue'],
        'backend': ['back-end', 'server-side', 'api', 'microservices']
    }
    
    required_canon = [canon(skill) for skill in required_skills]
    candidate_canon = [canon(skill) for skill in candidate_skills]
    
    matched = []
    missing = []
    
    for req_skill in required_canon:
        best_match = 0
        matched_skill = None
        
        # Direct fuzzy matching
        for cand_skill in candidate_canon:
            score = fuzz.token_sort_ratio(req_skill, cand_skill)
            if score > best_match:
                best_match = score
                matched_skill = cand_skill
        
        # Check synonyms
        for canonical, synonyms in skill_synonyms.items():
            if req_skill in synonyms or req_skill == canonical:
                for syn in synonyms + [canonical]:
                    for cand_skill in candidate_canon:
                        score = fuzz.token_sort_ratio(syn, cand_skill)
                        if score > best_match:
                            best_match = score
                            matched_skill = cand_skill
        
        if best_match >= threshold:
            matched.append(req_skill)
        else:
            missing.append(req_skill)
    
    match_percentage = int(100 * len(matched) / len(required_skills)) if required_skills else 100
    return matched, missing, match_percentage

def education_score(required_education: List[str], candidate_education: List[Dict]) -> Tuple[int, str]:
    """Score education match"""
    if not required_education:
        return 100, "No specific education requirements"
    
    if not candidate_education:
        return 0, "No education information found"
    
    # Extract degree levels
    degree_hierarchy = {
        'phd': 5, 'doctorate': 5,
        'master': 4, 'mtech': 4, 'mba': 4, 'msc': 4, 'mcom': 4, 'ma': 4,
        'bachelor': 3, 'btech': 3, 'be': 3, 'bsc': 3, 'bcom': 3, 'ba': 3, 'bca': 3,
        'diploma': 2,
        'certificate': 1
    }
    
    required_level = 0
    for edu in required_education:
        for degree, level in degree_hierarchy.items():
            if degree in edu.lower():
                required_level = max(required_level, level)
    
    candidate_level = 0
    for edu in candidate_education:
        degree_text = edu.get('degree', '').lower()
        for degree, level in degree_hierarchy.items():
            if degree in degree_text:
                candidate_level = max(candidate_level, level)
    
    if candidate_level >= required_level:
        return 100, "Education requirements met"
    elif candidate_level >= required_level - 1:
        return 75, "Close match to education requirements"
    else:
        return 25, "Education requirements not fully met"

def experience_score(required_experience: str, candidate_experience: List[Dict]) -> Tuple[int, str]:
    """Score experience match"""
    if not required_experience or 'not specified' in required_experience.lower():
        return 100, "No specific experience requirements"
    
    # Extract years from requirement
    req_years = 0
    req_match = re.search(r'(\d+)', required_experience)
    if req_match:
        req_years = int(req_match.group(1))
    
    # Estimate candidate experience (rough estimation)
    candidate_years = len(candidate_experience) * 1.5  # Assume 1.5 years per job on average
    
    if candidate_years >= req_years:
        return 100, f"Experience requirement met ({candidate_years:.1f} years)"
    elif candidate_years >= req_years * 0.7:
        return 75, f"Close to experience requirement ({candidate_years:.1f} years)"
    else:
        return 40, f"Below experience requirement ({candidate_years:.1f} years)"

def project_relevance_score(candidate_projects: List[Dict], job_skills: List[str]) -> Tuple[int, str]:
    """Score project relevance to job requirements"""
    if not candidate_projects:
        return 50, "No projects found"
    
    if not job_skills:
        return 80, "Projects present but no specific skills to match"
    
    total_relevance = 0
    relevant_projects = 0
    
    for project in candidate_projects:
        project_text = f"{project.get('title', '')} {project.get('description', '')}".lower()
        project_relevance = 0
        
        for skill in job_skills:
            if canon(skill) in project_text:
                project_relevance += 1
        
        if project_relevance > 0:
            relevant_projects += 1
            total_relevance += min(project_relevance / len(job_skills), 1.0) * 100
    
    if relevant_projects == 0:
        return 30, "No relevant projects found"
    
    avg_score = int(total_relevance / relevant_projects)
    return avg_score, f"{relevant_projects} relevant projects found"

def comprehensive_scoring(resume_data: Dict, job_data: Dict) -> Dict:
    """Comprehensive scoring system with multiple criteria"""
    # Extract data
    resume_skills = resume_data.get('skills', [])
    resume_education = resume_data.get('education', [])
    resume_experience = resume_data.get('experience', [])
    resume_projects = resume_data.get('projects', [])
    resume_certifications = resume_data.get('certifications', [])
    
    job_must_have = job_data.get('must_have_skills', [])
    job_nice_to_have = job_data.get('nice_to_have_skills', [])
    job_education = job_data.get('required_education', [])
    job_experience = job_data.get('required_experience', '')
    
    # Calculate individual scores
    matched_must, missing_must, must_have_score = advanced_skill_matching(job_must_have, resume_skills)
    matched_nice, missing_nice, nice_to_have_score = advanced_skill_matching(job_nice_to_have, resume_skills, threshold=60)
    
    edu_score, edu_feedback = education_score(job_education, resume_education)
    exp_score, exp_feedback = experience_score(job_experience, resume_experience)
    project_score, project_feedback = project_relevance_score(resume_projects, job_must_have + job_nice_to_have)
    
    # Certification bonus
    cert_bonus = min(len(resume_certifications) * 5, 20)  # Max 20 points bonus
    
    # Weighted final score
    weights = {
        'must_have_skills': 0.35,
        'nice_to_have_skills': 0.15,
        'education': 0.20,
        'experience': 0.20,
        'projects': 0.10
    }
    
    weighted_score = (
        must_have_score * weights['must_have_skills'] +
        nice_to_have_score * weights['nice_to_have_skills'] +
        edu_score * weights['education'] +
        exp_score * weights['experience'] +
        project_score * weights['projects']
    )
    
    final_score = min(int(weighted_score + cert_bonus), 100)
    
    return {
        'final_score': final_score,
        'must_have_score': must_have_score,
        'nice_to_have_score': nice_to_have_score,
        'education_score': edu_score,
        'experience_score': exp_score,
        'project_score': project_score,
        'certification_bonus': cert_bonus,
        'matched_must_have': matched_must,
        'missing_must_have': missing_must,
        'matched_nice_to_have': matched_nice,
        'missing_nice_to_have': missing_nice,
        'education_feedback': edu_feedback,
        'experience_feedback': exp_feedback,
        'project_feedback': project_feedback,
        'verdict': verdict_from_score(final_score)
    }

def semantic_score(jd_text, resume_text):
    """Calculate semantic similarity using embeddings"""
    try:
        if not genai:
            return 50  # Fallback score if genai not available
            
        # Use text embedding model
        jd_result = genai.embed_content(
            model="models/embedding-001",
            content=jd_text,
            task_type="retrieval_document"
        )
        
        resume_result = genai.embed_content(
            model="models/embedding-001", 
            content=resume_text,
            task_type="retrieval_query"
        )
        
        v1 = np.array(jd_result['embedding'])
        v2 = np.array(resume_result['embedding'])
        
        cos = float(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)+1e-12))
        return int(round((cos+1)/2*100))
    except Exception as e:
        print(f"Semantic scoring error: {e}")
        return 50  # Fallback score

def compute_final_score(hard, semantic, hard_weight=0.6, semantic_weight=0.4):
    return int(round(hard*hard_weight + semantic*semantic_weight))

def verdict_from_score(score):
    if score >= 80: return "High"
    if score >= 60: return "Medium"
    return "Low"

def generate_comprehensive_feedback(scoring_results: Dict, resume_data: Dict, job_data: Dict) -> str:
    """Generate comprehensive, actionable feedback for candidates"""
    feedback_sections = []
    
    # Overall Performance
    score = scoring_results['final_score']
    verdict = scoring_results['verdict']
    
    if score >= 80:
        feedback_sections.append(f"🎉 Excellent match! Your profile scores {score}/100 with a {verdict} suitability rating.")
    elif score >= 60:
        feedback_sections.append(f"✅ Good match! Your profile scores {score}/100 with a {verdict} suitability rating.")
    else:
        feedback_sections.append(f"📈 Areas for improvement. Your profile scores {score}/100 with a {verdict} suitability rating.")
    
    # Skills Analysis
    if scoring_results['missing_must_have']:
        feedback_sections.append(f"\n🔴 Critical Skills Gap:\n" + 
                               "\n".join([f"• {skill}" for skill in scoring_results['missing_must_have'][:5]]))
        feedback_sections.append("Prioritize learning these essential skills for this role.")
    
    if scoring_results['matched_must_have']:
        feedback_sections.append(f"\n🟢 Strong Skills Match:\n" + 
                               "\n".join([f"• {skill}" for skill in scoring_results['matched_must_have'][:5]]))
    
    if scoring_results['missing_nice_to_have']:
        feedback_sections.append(f"\n🟡 Nice-to-Have Skills:\n" + 
                               "\n".join([f"• {skill}" for skill in scoring_results['missing_nice_to_have'][:3]]) +
                               "\nThese would strengthen your profile.")
    
    # Education Feedback
    if scoring_results['education_score'] < 75:
        feedback_sections.append(f"\n📚 Education: {scoring_results['education_feedback']}")
    
    # Experience Feedback
    if scoring_results['experience_score'] < 75:
        feedback_sections.append(f"\n💼 Experience: {scoring_results['experience_feedback']}")
    
    # Project Feedback
    if scoring_results['project_score'] < 60:
        feedback_sections.append(f"\n🚀 Projects: {scoring_results['project_feedback']}")
        feedback_sections.append("Consider adding projects that demonstrate the required skills.")
    
    # Certification Recommendations
    if scoring_results['certification_bonus'] < 10:
        relevant_certs = suggest_certifications(job_data.get('must_have_skills', []))
        if relevant_certs:
            feedback_sections.append(f"\n🏆 Recommended Certifications:\n" + 
                                   "\n".join([f"• {cert}" for cert in relevant_certs[:3]]))
    
    # Improvement Action Plan
    if score < 70:
        feedback_sections.append(generate_action_plan(scoring_results, job_data))
    
    return "\n".join(feedback_sections)

def suggest_certifications(skills: List[str]) -> List[str]:
    """Suggest relevant certifications based on required skills"""
    cert_mapping = {
        'aws': ['AWS Certified Solutions Architect', 'AWS Certified Developer'],
        'azure': ['Microsoft Azure Fundamentals', 'Azure Developer Associate'],
        'gcp': ['Google Cloud Professional Cloud Architect'],
        'python': ['Python Institute PCAP', 'Microsoft Python Certification'],
        'java': ['Oracle Java SE Certification', 'Spring Professional'],
        'javascript': ['Microsoft JavaScript Certification'],
        'react': ['Meta React Developer Certificate'],
        'machine learning': ['AWS Machine Learning Specialty', 'Google ML Engineer'],
        'data science': ['IBM Data Science Professional', 'Microsoft Data Scientist Associate'],
        'sql': ['Microsoft SQL Server Certification', 'Oracle Database Certification']
    }
    
    suggestions = []
    for skill in skills:
        skill_lower = skill.lower()
        for key, certs in cert_mapping.items():
            if key in skill_lower:
                suggestions.extend(certs)
    
    return list(set(suggestions))[:5]  # Return unique suggestions, max 5

def generate_action_plan(scoring_results: Dict, job_data: Dict) -> str:
    """Generate a prioritized action plan for improvement"""
    plan = ["\n📋 Action Plan for Improvement:"]
    
    # Priority 1: Critical missing skills
    if scoring_results['missing_must_have']:
        plan.append("\n1. 🎯 PRIORITY: Learn critical skills")
        for i, skill in enumerate(scoring_results['missing_must_have'][:3], 1):
            plan.append(f"   {i}.{i} Focus on {skill}")
    
    # Priority 2: Projects
    if scoring_results['project_score'] < 60:
        plan.append("\n2. 🚀 Build relevant projects")
        plan.append("   - Create 2-3 projects showcasing the missing skills")
        plan.append("   - Document projects on GitHub with clear README")
    
    # Priority 3: Experience/Education
    if scoring_results['experience_score'] < 60:
        plan.append("\n3. 💼 Gain practical experience")
        plan.append("   - Look for internships or freelance opportunities")
        plan.append("   - Contribute to open-source projects")
    
    # Priority 4: Certifications
    if scoring_results['certification_bonus'] < 10:
        plan.append("\n4. 🏆 Consider relevant certifications")
        plan.append("   - Start with fundamental certifications in your tech stack")
    
    return "\n".join(plan)

def generate_feedback(missing_skills, matched_skills):
    """Legacy function for backward compatibility"""
    lines = []
    if missing_skills:
        lines.append("Missing skills: " + ", ".join(missing_skills))
    else:
        lines.append("Good skill match.")
    if matched_skills:
        lines.append("Top skills: " + ", ".join(matched_skills[:5]))
    return " | ".join(lines)
