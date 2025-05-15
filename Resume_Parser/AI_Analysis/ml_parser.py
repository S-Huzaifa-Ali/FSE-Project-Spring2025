import re
import os
import nltk
import spacy
import PyPDF2
from typing import Dict, List, Any, Optional
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import docx

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    print("SpaCy model not available. Using fallback extraction methods.")

COMMON_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust",
    "typescript", "scala", "perl", "r", "matlab", "bash", "shell", "powershell", "sql", "html", "css",

    "react", "angular", "vue", "django", "flask", "spring", "node.js", "express", "laravel",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "bootstrap", "jquery",

    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "sql server", "redis", "cassandra",

    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "bitbucket",
    "terraform", "ansible", "puppet", "chef", "ci/cd", "devops",

    "machine learning", "deep learning", "data science", "data analysis", "data visualization",
    "statistics", "big data", "hadoop", "spark", "tableau", "power bi", "data mining",

    "android", "ios", "react native", "flutter", "xamarin", "mobile development",

    "rest api", "graphql", "microservices", "serverless", "blockchain", "web development",
    "full stack", "front end", "back end", "testing", "qa", "agile", "scrum", "jira",

    "communication", "teamwork", "leadership", "problem solving", "critical thinking",
    "time management", "project management", "creativity", "adaptability", "collaboration"
]

def extract_text_from_docx(file_path: str) -> str:
    text = ""
    
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        print(f"Successfully extracted text from DOCX: {len(text)} characters")
    except Exception as e:
        print(f"DOCX extraction failed: {str(e)}")
    
    return text

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        return text
        
    if not os.access(file_path, os.R_OK):
        print(f"Error: File exists but is not readable: {file_path}")
        return text
    
    try:
        text = extract_text(file_path)
        print(f"Successfully extracted text with pdfminer: {len(text)} characters")
    except Exception as e:
        print(f"pdfminer extraction failed: {str(e)}")
    
    if not text or len(text) < 100:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                print(f"Successfully extracted text with PyPDF2: {len(text)} characters")
        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
    
    if not text:
        print(f"Warning: Could not extract any text from file: {file_path}")
        
    return text

def extract_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"Error: File does not exist at path: {file_path}")
        return ""
        
    if not os.access(file_path, os.R_OK):
        print(f"Error: File exists but is not readable: {file_path}")
        return ""
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_ext}")
        return ""

def preprocess_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\n]', ' ', text)
    return text

def extract_contact_info(text: str) -> Dict[str, str]:
    contact_info = {
        'email': None,
        'phone': None,
    }
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        contact_info['email'] = email_matches[0]
    
    phone_pattern = r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        contact_info['phone'] = phone_matches[0]
    
    return contact_info

def extract_skills(text: str) -> List[str]:
    skills = []
    text_lower = text.lower()
    
    if SPACY_AVAILABLE:
        doc = nlp(text)
        for chunk in doc.noun_chunks:
            if chunk.text.lower() in COMMON_SKILLS:
                skills.append(chunk.text)
    
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.append(skill)
    
    skills_section_pattern = re.compile(r'(?:skills|technical skills|technical|programming|languages|frameworks|tools|technologies|competencies|proficiencies)[:\-]?\s*(.+?)(?=\n\n|$)', re.I | re.S)
    
    for skills_match in skills_section_pattern.finditer(text):
        skills_text = skills_match.group(1)
        
        category_pattern = re.compile(r'([\w\s]+):\s*([^\n]+)', re.I)
        category_matches = category_pattern.findall(skills_text)
        
        if category_matches:
            for _, category_skills in category_matches:
                for skill_candidate in re.split(r'[,;•|/]', category_skills):
                    skill_candidate = skill_candidate.strip().lower()
                    if skill_candidate in COMMON_SKILLS and skill_candidate not in skills:
                        skills.append(skill_candidate)
        else:
            for skill_candidate in re.split(r'[,;•|/\n]', skills_text):
                skill_candidate = skill_candidate.strip().lower()
                if skill_candidate in COMMON_SKILLS and skill_candidate not in skills:
                    skills.append(skill_candidate)
    
    bullet_pattern = re.compile(r'(?:^|\n)[•\*\-]\s*([^\n]+)', re.M)
    for bullet_match in bullet_pattern.finditer(text):
        bullet_text = bullet_match.group(1).lower()
        for skill in COMMON_SKILLS:
            if skill in bullet_text:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, bullet_text) and skill not in skills:
                    skills.append(skill)
    
    normalized_skills = []
    for skill in skills:
        skill = skill.strip().lower()
        if skill and skill not in normalized_skills:
            normalized_skills.append(skill)
    
    return normalized_skills

def extract_education(text: str) -> List[Dict[str, str]]:
    education = []
    
    edu_section_pattern = re.compile(r'education[:\-]\s*(.+?)(?=\n\n|$)', re.I | re.S)
    if edu_match := edu_section_pattern.search(text):
        edu_text = edu_match.group(1)
        
        edu_entries = re.split(r'\n(?=\d{4}|\w+\s+\d{4}|university|college|institute|school)', edu_text, flags=re.I)
        
        for entry in edu_entries:
            if not entry.strip():
                continue
                
            edu_info = {'raw': entry.strip()}
            
            degree_pattern = r'(bachelor|master|phd|doctorate|b\.?\s*[a-z]*|m\.?\s*[a-z]*|ph\.?\s*d\.?)[^\n]*', re.I
            if degree_match := re.search(degree_pattern, entry):
                edu_info['degree'] = degree_match.group(0).strip()
            
            inst_pattern = r'(university|college|institute|school)[^\n]*', re.I
            if inst_match := re.search(inst_pattern, entry):
                edu_info['institution'] = inst_match.group(0).strip()
            
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, entry)
            if years:
                edu_info['year'] = years[-1]
            
            education.append(edu_info)
    
    return education

def extract_experience(text: str) -> List[Dict[str, str]]:
    experience = []
    
    exp_section_pattern = re.compile(r'(experience|work\s+experience|employment)[:\-]\s*(.+?)(?=\n\n|$)', re.I | re.S)
    if exp_match := exp_section_pattern.search(text):
        exp_text = exp_match.group(2)
        
        exp_entries = re.split(r'\n(?=\d{4}|\w+\s+\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', exp_text, flags=re.I)
        
        for entry in exp_entries:
            if not entry.strip():
                continue
                
            exp_info = {'raw': entry.strip()}
            
            company_lines = entry.split('\n')
            if company_lines:
                exp_info['company'] = company_lines[0].strip()
            
            position_pattern = r'(developer|engineer|manager|director|analyst|designer|consultant|specialist|coordinator)[^\n]*', re.I
            if position_match := re.search(position_pattern, entry):
                exp_info['position'] = position_match.group(0).strip()
            
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, entry)
            if len(years) >= 2:
                exp_info['start_year'] = years[0]
                exp_info['end_year'] = years[1]
            elif len(years) == 1:
                exp_info['year'] = years[0]
            
            duration_pattern = r'(\d+)\s+(year|month)s?'
            if duration_match := re.search(duration_pattern, entry, re.I):
                exp_info['duration'] = duration_match.group(0)
            
            experience.append(exp_info)
    
    return experience

def extract_projects(text: str) -> List[Dict[str, str]]:
    projects = []
    
    proj_section_pattern = re.compile(r'projects?[:\-]\s*(.+?)(?=\n\n|$)', re.I | re.S)
    if proj_match := proj_section_pattern.search(text):
        proj_text = proj_match.group(1)
        
        proj_entries = re.split(r'\n(?=•|\*|\-|\d+\.)', proj_text)
        
        for entry in proj_entries:
            if not entry.strip():
                continue
                
            proj_info = {'raw': entry.strip()}
            
            lines = entry.split('\n')
            if lines:
                proj_info['name'] = lines[0].strip().strip('•*-')
            
            tech_pattern = r'(using|with|built\s+with|developed\s+with|technologies?)[^\n]*', re.I
            if tech_match := re.search(tech_pattern, entry):
                proj_info['technologies'] = tech_match.group(0).strip()
            
            projects.append(proj_info)
    
    return projects

def extract_qualification(text: str) -> str:
    education = extract_education(text)
    
    qualification_rank = {
        'phd': 5,
        'doctorate': 5,
        'ph.d': 5,
        'master': 4,
        'mba': 4,
        'ms': 4,
        'ma': 4,
        'm.': 4,
        'bachelor': 3,
        'bs': 3,
        'ba': 3,
        'b.': 3,
        'associate': 2,
        'diploma': 1,
        'certificate': 0
    }
    
    highest_qual = None
    highest_rank = -1
    
    for edu in education:
        if 'degree' in edu:
            degree_lower = edu['degree'].lower()
            for qual, rank in qualification_rank.items():
                if qual in degree_lower and rank > highest_rank:
                    highest_qual = edu['degree']
                    highest_rank = rank
    
    if highest_qual:
        return highest_qual
    
    for qual, rank in qualification_rank.items():
        if re.search(r'\b' + re.escape(qual) + r'\b', text, re.I):
            if rank > highest_rank:
                highest_qual = qual.title()
                highest_rank = rank
    
    return highest_qual or "Not specified"

def parse_resume_ml(file_path: str) -> Dict[str, Any]:
    try:
        text = extract_text_from_file(file_path)
        
        processed_text = preprocess_text(text)
        
        contact_info = extract_contact_info(processed_text)
        skills = extract_skills(processed_text)
        education = extract_education(processed_text)
        experience = extract_experience(processed_text)
        projects = extract_projects(processed_text)
        qualification = extract_qualification(processed_text)
        name = extract_name(processed_text)
        
        education_dict = {}
        for i, edu in enumerate(education):
            key = f"education_{i+1}"
            education_dict[key] = edu
        
        experience_dict = {}
        for i, exp in enumerate(experience):
            key = f"experience_{i+1}"
            experience_dict[key] = exp
            
        projects_dict = {}
        for i, proj in enumerate(projects):
            key = f"project_{i+1}"
            projects_dict[key] = proj
        
        relevant_skills = [skill for skill in skills if skill.lower() in [s.lower() for s in COMMON_SKILLS[:30]]]
        
        match_score = min(len(skills) * 5, 70)
        if qualification and any(q in qualification.lower() for q in ['master', 'phd', 'doctorate']):
            match_score += 15
        elif qualification and any(q in qualification.lower() for q in ['bachelor', 'b.s', 'b.a']):
            match_score += 10
        
        match_score = min(match_score, 100)
        
        parsed_data = {
            'name': name,
            'skills': skills,
            'relevant_skills': relevant_skills,
            'education': education_dict,
            'experience': experience_dict,
            'projects': projects_dict,
            'qualification': qualification,
            'email': contact_info.get('email'),
            'phone': contact_info.get('phone'),
            'match_score': match_score,
            'resume_path': file_path.replace('\\', '/').split('media/')[-1] if 'media/' in file_path else None
        }
        
        return parsed_data
        
    except Exception as e:
        print(f'Error parsing resume with ML: {str(e)}')
        return {
            'name': None,
            'skills': [],
            'relevant_skills': [],
            'education': {},
            'experience': {},
            'projects': {},
            'qualification': "Not specified",
            'email': None,
            'phone': None,
            'match_score': 0,
            'resume_path': file_path.replace('\\', '/').split('media/')[-1] if 'media/' in file_path else None
        }

def extract_name(text: str) -> Optional[str]:
    lines = text.split('\n')
    
    for line in lines[:5]:
        line = line.strip()
        if not line:
            continue
            
        if any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'vitae', 'email', 'phone', 'address']):
            continue
            
        if re.match(r'^[A-Za-z\s\.]+$', line) and len(line) < 40:
            return line
    
    if SPACY_AVAILABLE:
        doc = nlp(text[:1000])
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
    
    return None

def filter_by_keyword_ml(parsed_list: List[Dict], keyword: str) -> List[Dict]:
    if not keyword or not keyword.strip():
        return parsed_list
        
    kw = keyword.strip().lower()
    filtered_results = []
    
    for resume in parsed_list:
        skills_match = any(kw in skill.lower() for skill in resume.get('skills', []))
        
        education_match = False
        for edu in resume.get('education', []):
            if isinstance(edu, dict) and any(kw in str(value).lower() for value in edu.values()):
                education_match = True
                break
        
        experience_match = False
        for exp in resume.get('experience', []):
            if isinstance(exp, dict) and any(kw in str(value).lower() for value in exp.values()):
                experience_match = True
                break
        
        projects_match = False
        for proj in resume.get('projects', []):
            if isinstance(proj, dict) and any(kw in str(value).lower() for value in proj.values()):
                projects_match = True
                break
        
        qualification_match = kw in str(resume.get('qualification', '')).lower()
        
        if skills_match or education_match or experience_match or projects_match or qualification_match:
            match_score = 0
            if skills_match:
                matching_skills = [skill for skill in resume.get('skills', []) if kw in skill.lower()]
                match_score += len(matching_skills) * 10
            
            if education_match:
                match_score += 5
            
            if experience_match:
                match_score += 7
            
            if projects_match:
                match_score += 3
            
            if qualification_match:
                match_score += 5
            
            resume_with_score = resume.copy()
            resume_with_score['match_score'] = min(match_score, 100)
            resume_with_score['relevant_skills'] = [skill for skill in resume.get('skills', []) if kw in skill.lower()]
            
            filtered_results.append(resume_with_score)
    
    return sorted(filtered_results, key=lambda x: x.get('match_score', 0), reverse=True)