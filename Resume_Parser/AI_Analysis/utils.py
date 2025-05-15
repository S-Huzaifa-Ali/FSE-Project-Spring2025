import re
import os
from typing import Dict, List, Optional
from pdfminer.high_level import extract_text
from .ml_parser import parse_resume_ml, filter_by_keyword_ml

def parse_resume(file_path: str) -> Dict:

    default_data = {
        'skills': [],
        'education': {},
        'experience': {},
        'projects': {},
        'qualification': "Not specified",
        'email': None,
        'phone': None,
        'resume_path': file_path.replace('\\', '/').split('media/')[-1] if 'media/' in file_path else file_path
    }
    
    print(f'Original resume path: {file_path}')
    
    if not file_path:
        print("Error: Empty file path provided")
        return default_data
    
    file_path = file_path.replace('\\', '/')
    
    if not os.path.isabs(file_path):
        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        print(f'Media root directory: {media_root}')
        
        if media_root:
            possible_paths = [
                os.path.join(media_root, file_path),
                os.path.join(media_root, file_path.lstrip('/')),
                os.path.join(media_root, file_path.lstrip('/media/')),
                os.path.join(settings.BASE_DIR, 'media', file_path),
                os.path.join(media_root, os.path.basename(file_path))
            ]
            
            for path in possible_paths:
                print(f'Checking possible path: {path}')
                if os.path.exists(path):
                    file_path = path
                    print(f'Found resume at path: {file_path}')
                    break
    
    if not os.path.exists(file_path):
        print(f'Resume file not found at path: {file_path}')
        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        
        file_name = os.path.basename(file_path)
        print(f'Searching for file by name: {file_name}')
        found = False
        
        for root, dirs, files in os.walk(media_root):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                print(f'Found resume by filename at: {file_path}')
                found = True
                break
        
        if not found:
            print(f'Warning: Could not find resume file {file_name} anywhere in {media_root}')
            return default_data
        
    try:
        parsed_data = parse_resume_ml(file_path)
        
        if not parsed_data.get('skills') and not parsed_data.get('education') and not parsed_data.get('experience'):
            print(f'Warning: No meaningful data extracted from resume at {file_path}')
            parsed_data['resume_path'] = file_path.replace('\\', '/').split('media/')[-1] if 'media/' in file_path else file_path
            
        for field in ['skills', 'education', 'experience', 'projects', 'qualification', 'email', 'phone']:
            if field not in parsed_data:
                if field == 'skills':
                    parsed_data[field] = []
                elif field in ['education', 'experience', 'projects']:
                    parsed_data[field] = {}
                elif field == 'qualification':
                    parsed_data[field] = "Not specified"
                else:
                    parsed_data[field] = None
            elif parsed_data[field] is None and field in ['education', 'experience', 'projects']:
                parsed_data[field] = {}
            elif parsed_data[field] is None and field == 'skills':
                parsed_data[field] = []
                
        if 'resume_path' not in parsed_data or not parsed_data['resume_path']:
            parsed_data['resume_path'] = file_path.replace('\\', '/').split('media/')[-1] if 'media/' in file_path else file_path
            
        print(f'Successfully parsed resume with {len(parsed_data.get("skills", []))} skills')
        return parsed_data
        
    except Exception as e:
        print(f'Error parsing resume: {str(e)}')
        return default_data

def filter_by_keyword(parsed_list: List[Dict], keyword: str) -> List[Dict]:

    kw = keyword.strip().lower()
    return [p for p in parsed_list if any(kw in skill.lower() for skill in p.get('skills', []))]
