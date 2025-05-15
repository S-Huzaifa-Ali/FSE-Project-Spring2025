from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Application
import os
import mimetypes

@login_required
def serve_resume_file(request, application_id):
    """
    Securely serve resume files to authorized users
    """
    try:
        application = Application.objects.get(id=application_id)
        
        if request.user.user_type == 'candidate':
            if application.candidate.user != request.user:
                raise Http404("You don't have permission to access this resume")
        elif request.user.user_type == 'recruiter':
            if application.job.recruiter != request.user:
                raise Http404("You don't have permission to access this resume")
        else:
            raise Http404("Access denied")
        
        if not application.resume:
            raise Http404("No resume attached to this application")
        
        try:
            file_path = None
            
            try:
                if hasattr(application.resume, 'path'):
                    absolute_path = application.resume.path
                    if os.path.exists(absolute_path):
                        file_path = absolute_path
            except Exception as path_error:
                print(f"Error accessing absolute path: {str(path_error)}")
            
            if not file_path:
                try:
                    relative_path = str(application.resume.name).replace('\\', '/')
                    if relative_path.startswith('media/'):
                        relative_path = relative_path[6:]
                    media_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    
                    if os.path.exists(media_path):
                        file_path = media_path
                except Exception as name_error:
                    print(f"Error with relative path: {str(name_error)}")
            
            if not file_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    media_path = os.path.join(settings.MEDIA_ROOT, 'applications', 'resumes', filename)
                    
                    if os.path.exists(media_path):
                        file_path = media_path
                except Exception as filename_error:
                    print(f"Error with filename in applications/resumes: {str(filename_error)}")
            
            if not file_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    found = False
                    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                        if filename in files:
                            file_path = os.path.join(root, filename)
                            found = True
                            break
                except Exception as search_error:
                    print(f"Error searching for file: {str(search_error)}")
            
            if not file_path:
                raise Http404(f"Resume file not found: {application.resume.name}")
            
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            disposition = request.GET.get('disposition', 'attachment')
            response['Content-Disposition'] = f'{disposition}; filename="{os.path.basename(file_path)}"'
            return response
            
        except Exception as e:
            raise Http404(f"Error accessing resume file: {str(e)}")
            
    except Application.DoesNotExist:
        raise Http404("Application not found")