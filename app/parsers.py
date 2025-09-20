import pdfplumber
from docx import Document
import re
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

# Initialize Gemini for AI-powered parsing
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
except ImportError:
    genai = None

def extract_text_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)

def extract_text_docx(path: str) -> str:
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except:
        return ""

def normalize_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"Page \d+ of \d+", "", text, flags=re.I)
    return text.strip()

def parse_skills(text: str) -> List[str]:
    """Enhanced skill extraction from resume text"""
    skills = set()
    text_lower = text.lower()
    lines = text_lower.splitlines()
    
    # Common technical skills to look for
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'postgresql',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'data science',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django',
        'fastapi', 'html', 'css', 'git', 'linux', 'windows', 'excel', 'tableau', 'powerbi',
        'spring boot', 'microservices', 'restful api', 'graphql', 'redis', 'elasticsearch'
    ]
    
    # Look for skills in dedicated sections
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in ['skills', 'technologies', 'tools', 'programming']):
            # Extract from current and next few lines
            for j in range(i, min(i + 5, len(lines))):
                parts = re.split(r'[,;\n|•\\-•]+', lines[j])
                for part in parts:
                    clean_part = part.strip()
                    if len(clean_part) > 1 and clean_part not in ['skills', 'technologies', 'tools']:
                        skills.add(clean_part)
    
    # Look for common technical skills throughout the text
    for skill in tech_skills:
        if skill in text_lower:
            skills.add(skill)
    
    return list(skills)

def parse_education(text: str) -> List[Dict]:
    """Extract education information from resume"""
    education = []
    lines = text.splitlines()
    
    degree_patterns = [
        r'(bachelor|master|phd|doctorate|b\.?tech|m\.?tech|b\.?e|m\.?e|bca|mca|mba|b\.?sc|m\.?sc|b\.?com|m\.?com)',
        r'(diploma|certificate)'
    ]
    
    year_pattern = r'(19|20)\d{2}'
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ['education', 'qualification', 'academic']):
            # Look in next 10 lines for education details
            for j in range(i+1, min(i+11, len(lines))):
                current_line = lines[j].strip()
                if not current_line:
                    continue
                    
                for pattern in degree_patterns:
                    if re.search(pattern, current_line.lower()):
                        # Extract year if present
                        year_match = re.search(year_pattern, current_line)
                        year = year_match.group() if year_match else None
                        
                        education.append({
                            'degree': current_line,
                            'year': year,
                            'institution': lines[j+1].strip() if j+1 < len(lines) else None
                        })
                        break
    
    return education

def parse_experience(text: str) -> List[Dict]:
    """Extract work experience from resume"""
    experience = []
    lines = text.splitlines()
    
    # Experience section indicators
    exp_indicators = ['experience', 'work history', 'employment', 'career', 'professional']
    
    # Date patterns
    date_patterns = [
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(19|20)\d{2}',
        r'(19|20)\d{2}\s*-\s*(19|20)\d{2}',
        r'(19|20)\d{2}\s*to\s*(19|20)\d{2}|present'
    ]
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in exp_indicators):
            # Look for experience entries in subsequent lines
            for j in range(i+1, min(i+20, len(lines))):
                current_line = lines[j].strip()
                if not current_line:
                    continue
                
                # Check if line contains date pattern (likely an experience entry)
                for pattern in date_patterns:
                    if re.search(pattern, current_line.lower()):
                        # Try to extract company and role from surrounding lines
                        company = current_line
                        role = lines[j-1].strip() if j > 0 else None
                        
                        experience.append({
                            'role': role,
                            'company': company,
                            'duration': current_line
                        })
                        break
    
    return experience

def parse_certifications(text: str) -> List[str]:
    """Extract certifications from resume"""
    certifications = []
    text_lower = text.lower()
    lines = text_lower.splitlines()
    
    # Common certifications
    cert_keywords = [
        'aws', 'azure', 'gcp', 'google cloud', 'cisco', 'microsoft', 'oracle',
        'pmp', 'scrum', 'agile', 'itil', 'comptia', 'cissp', 'ceh', 'cisa',
        'certified', 'certification', 'certificate'
    ]
    
    for line in lines:
        if any(keyword in line for keyword in ['certification', 'certificate', 'certified']):
            # Extract certification details
            parts = re.split(r'[,;\n|•\\-]+', line)
            for part in parts:
                clean_part = part.strip()
                if len(clean_part) > 3:
                    certifications.append(clean_part)
        
        # Look for specific certification patterns
        for cert in cert_keywords:
            if cert in line and len(line.strip()) < 100:  # Avoid long descriptions
                certifications.append(line.strip())
    
    return list(set(certifications))

def parse_projects(text: str) -> List[Dict]:
    """Extract project information from resume"""
    projects = []
    lines = text.splitlines()
    
    project_indicators = ['project', 'portfolio', 'github', 'work sample']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in project_indicators):
            # Look for project details in next few lines
            for j in range(i+1, min(i+15, len(lines))):
                current_line = lines[j].strip()
                if not current_line or len(current_line) < 10:
                    continue
                
                # If line looks like a project title (not too long, not a sentence)
                if len(current_line) < 100 and not current_line.endswith('.'):
                    description_lines = []
                    # Get description from next few lines
                    for k in range(j+1, min(j+4, len(lines))):
                        if lines[k].strip():
                            description_lines.append(lines[k].strip())
                    
                    projects.append({
                        'title': current_line,
                        'description': ' '.join(description_lines)[:200]  # Limit description
                    })
    
    return projects

def parse_resume_structured(text: str) -> Dict:
    """Parse resume into structured format with all components"""
    return {
        'raw_text': text,
        'skills': parse_skills(text),
        'education': parse_education(text),
        'experience': parse_experience(text),
        'certifications': parse_certifications(text),
        'projects': parse_projects(text),
        'parsed_at': datetime.utcnow().isoformat()
    }

def parse_job_description(jd_text: str) -> Dict:
    """Parse job description into structured format - simplified version"""
    return parse_job_description_fallback(jd_text)

def parse_job_description_fallback(jd_text: str) -> Dict:
    """Fallback rule-based job description parsing"""
    jd_lower = jd_text.lower()
    lines = jd_text.splitlines()
    
    # Extract title (usually first significant line)
    title = "Software Engineer"  # Default
    for line in lines[:5]:
        if line.strip() and len(line.strip()) < 100:
            title = line.strip()
            break
    
    # Common technical skills to look for
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb', 'postgresql',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'data science',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'flask', 'django',
        'fastapi', 'html', 'css', 'git', 'linux', 'windows', 'excel', 'tableau', 'powerbi',
        'spring boot', 'microservices', 'restful api', 'graphql', 'redis', 'elasticsearch'
    ]
    
    must_have = []
    nice_to_have = []
    
    # Look for required/must-have sections
    required_indicators = ['required', 'must have', 'essential', 'mandatory']
    preferred_indicators = ['preferred', 'nice to have', 'plus', 'bonus', 'desirable']
    
    current_section = 'must_have'
    for line in lines:
        line_lower = line.lower()
        
        # Determine section
        if any(indicator in line_lower for indicator in preferred_indicators):
            current_section = 'nice_to_have'
        elif any(indicator in line_lower for indicator in required_indicators):
            current_section = 'must_have'
        
        # Extract skills from line
        for skill in tech_skills:
            if skill in line_lower:
                if current_section == 'must_have' and skill not in must_have:
                    must_have.append(skill)
                elif current_section == 'nice_to_have' and skill not in nice_to_have:
                    nice_to_have.append(skill)
    
    # Extract experience requirements
    experience = "1-3 years"
    exp_patterns = [r'(\d+)[-\s]*(?:to|-)\s*(\d+)\s*years?', r'(\d+)\+?\s*years?']
    for pattern in exp_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            experience = match.group()
            break
    
    # Extract education requirements
    education = []
    edu_patterns = ['bachelor', 'master', 'phd', 'degree', 'b.tech', 'm.tech', 'computer science']
    for pattern in edu_patterns:
        if pattern in jd_lower:
            education.append(pattern.title())
    
    return {
        'title': title,
        'must_have_skills': must_have,
        'nice_to_have_skills': nice_to_have,
        'required_education': education,
        'required_experience': experience,
        'certifications': [],
        'responsibilities': [],
        'company_type': 'unknown',
        'location': 'not specified',
        'remote_friendly': 'remote' in jd_lower,
        'parsed_at': datetime.utcnow().isoformat()
    }
