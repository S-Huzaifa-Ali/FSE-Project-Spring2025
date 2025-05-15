import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resume_Parser.settings')
django.setup()

from django.conf import settings

def ensure_media_directories():
    """Ensure all required media directories exist with proper permissions"""
    print("Checking and creating media directories...")
    
    media_root = settings.MEDIA_ROOT
    print(f"Media root: {media_root}")
    
    if not os.path.exists(media_root):
        print(f"Creating media root directory: {media_root}")
        os.makedirs(media_root, exist_ok=True)
    
    applications_dir = os.path.join(media_root, 'applications')
    if not os.path.exists(applications_dir):
        print(f"Creating applications directory: {applications_dir}")
        os.makedirs(applications_dir, exist_ok=True)
    
    resumes_dir = os.path.join(applications_dir, 'resumes')
    if not os.path.exists(resumes_dir):
        print(f"Creating resumes directory: {resumes_dir}")
        os.makedirs(resumes_dir, exist_ok=True)
    
    try:
        os.chmod(media_root, 0o755)
        os.chmod(applications_dir, 0o755)
        os.chmod(resumes_dir, 0o755)
        print("Directory permissions set to 755 (rwxr-xr-x)")
    except Exception as e:
        print(f"Warning: Could not set permissions: {str(e)}")
    
    print("Media directories check complete.")
    return True

if __name__ == "__main__":
    ensure_media_directories()
    print("Done!")