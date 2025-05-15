from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Job, Recruiter
from .serializers import JobSerializer, RecruiterProfileSerializer, ApplicationSerializer
from Candidate.models import Resume, Application
from AI_Analysis.utils import parse_resume
from AI_Analysis.ml_parser import filter_by_keyword_ml
from AI_Analysis.serializers import ParsedResumeSerializer
import os

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)

class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(recruiter=self.request.user)

@login_required
def recruiter_dashboard_view(request):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        recruiter = Recruiter.objects.create(user=request.user, company_name='Company Name')
    
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    
    job_ids = jobs.values_list('id', flat=True)
    applications = Application.objects.filter(job_id__in=job_ids).order_by('-applied_at')
    
    total_applications = applications.count()
    
    total_jobs = jobs.count()
    
    context = {
        'recruiter': recruiter,
        'jobs': jobs,
        'recent_applications': applications[:5],
        'total_applications': total_applications,
        'total_jobs': total_jobs,
    }
    
    return render(request, 'recruiter/dashboard.html', context)

@login_required
def job_management_view(request):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    recruiter = Recruiter.objects.get(user=request.user)
    
    if request.method == 'POST':
        if 'job_id' in request.POST and request.POST.get('job_id').strip():
            job_id = request.POST.get('job_id')
            job = get_object_or_404(Job, id=job_id, recruiter=request.user)
            
            job.designation = request.POST.get('designation')
            job.company_name = request.POST.get('company_name')
            job.description = request.POST.get('description')
            
            skills = request.POST.get('required_skills', '')
            job.required_skills = [skill.strip() for skill in skills.split(',')] if skills else []
            
            job.experience_requirements = request.POST.get('experience_requirements', '')
            job.education_requirements = request.POST.get('education_requirements', '')
            
            job.save()
            messages.success(request, 'Job updated successfully!')
        else:
            designation = request.POST.get('designation')
            company_name = request.POST.get('company_name')
            description = request.POST.get('description')
            
            skills = request.POST.get('required_skills', '')
            required_skills = [skill.strip() for skill in skills.split(',')] if skills else []
            
            experience_requirements = request.POST.get('experience_requirements', '')
            education_requirements = request.POST.get('education_requirements', '')
            
            Job.objects.create(
                recruiter=request.user,
                designation=designation,
                company_name=company_name,
                description=description,
                required_skills=required_skills,
                experience_requirements=experience_requirements,
                education_requirements=education_requirements
            )
            
            messages.success(request, 'Job created successfully!')
    
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    
    context = {
        'recruiter': recruiter,
        'jobs': jobs,
    }
    
    return render(request, 'recruiter/job_management.html', context)

@login_required
def job_edit_view(request, job_id):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    
    if request.method == 'POST':
        job.designation = request.POST.get('designation')
        job.company_name = request.POST.get('company_name')
        job.description = request.POST.get('description')
        
        skills = request.POST.get('required_skills', '')
        job.required_skills = [skill.strip() for skill in skills.split(',')] if skills else []
        
        job.experience_requirements = request.POST.get('experience_requirements', '')
        job.education_requirements = request.POST.get('education_requirements', '')
        
        job.save()
        messages.success(request, 'Job updated successfully!')
        return redirect('job_management')
    
    context = {
        'job': job,
        'required_skills_str': ', '.join(job.required_skills),
    }
    
    return render(request, 'recruiter/job_edit.html', context)

@login_required
def job_delete_view(request, job_id):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('job_management')
    
    context = {
        'job': job,
    }
    
    return render(request, 'recruiter/job_delete.html', context)

@login_required
def resume_parser_view(request):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    parsed_resumes = []
    candidate_list = []
    keyword = ''
    search_performed = False
    
    recruiter_jobs = Job.objects.filter(recruiter=request.user).values_list('id', flat=True)
    applications = Application.objects.filter(job__id__in=recruiter_jobs)
    
    if applications.exists():
        for application in applications:
            if not application.resume:
                continue
                
            candidate_info = {
                'name': application.candidate.name,
                'application_id': application.id,
                'job_title': application.job.designation,
                'email': getattr(application.candidate.user, 'email', ''),
                'applied_at': application.applied_at,
            }
            candidate_list.append(candidate_info)
    
    if request.method == 'POST':
        search_performed = True
        keyword = request.POST.get('keyword', '').strip().lower()
        
        if not applications.exists():
            messages.error(request, 'No applications with resumes found in the system')
        else:
            for application in applications:
                try:
                    if not application.resume:
                        continue
                    
                    file_path = None
                    try:
                        if hasattr(application.resume, 'path'):
                            file_path = application.resume.path
                            if not os.path.exists(file_path):
                                file_path = None
                    except Exception as path_error:
                        print(f"Error accessing resume path: {str(path_error)}")
                    
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
                        print(f"Could not find resume file for application {application.id}")
                        continue
                    
                    resume_data = parse_resume(file_path)
                    
                    if resume_data:
                        resume_data['name'] = application.candidate.name
                        resume_data['application_id'] = application.id
                        resume_data['job_title'] = application.job.designation
                        resume_data['email'] = getattr(application.candidate.user, 'email', '')
                        resume_data['applied_at'] = application.applied_at
                        parsed_resumes.append(resume_data)
                except Exception as e:
                    print(f'Error parsing resume: {str(e)}')
            
            if keyword and parsed_resumes:
                filtered_resumes = filter_by_keyword_ml(parsed_resumes, keyword)
                
                if not filtered_resumes:
                    filtered_resumes = []
                    for resume in parsed_resumes:
                        skills_match = any(keyword in skill.lower() for skill in resume.get('skills', []))
                        exp_match = keyword in str(resume.get('experience', '')).lower()
                        edu_match = keyword in str(resume.get('education', '')).lower()
                        
                        if skills_match or exp_match or edu_match:
                            filtered_resumes.append(resume)
                
                parsed_resumes = filtered_resumes
    
    context = {
        'parsed_resumes': parsed_resumes,
        'candidate_list': candidate_list,
        'keyword': keyword,
        'search_performed': search_performed,
    }
    
    return render(request, 'recruiter/resume_parser.html', context)

@login_required
def application_detail_view(request, application_id):

    if request.user.user_type != 'recruiter':
        messages.error(request, 'Access denied. You are not a recruiter.')
        return redirect('home')
    
    application = get_object_or_404(Application, id=application_id)
    
    if application.job.recruiter != request.user:
        messages.error(request, 'Access denied. This application is not for your job.')
        return redirect('recruiter_dashboard')
    
    parsed_resume = None
    if application.resume:
        try:
            from django.conf import settings
            import os
            
            resume_path = None
            
            try:
                if hasattr(application.resume, 'path'):
                    absolute_path = application.resume.path
                    if os.path.exists(absolute_path):
                        resume_path = absolute_path
                        print(f'Found resume at absolute path: {resume_path}')
            except Exception as path_error:
                print(f"Error accessing absolute path: {str(path_error)}")
            
            if not resume_path:
                try:
                    relative_path = str(application.resume.name).replace('\\', '/')
                    if relative_path.startswith('media/'):
                        relative_path = relative_path[6:]
                    media_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    
                    if os.path.exists(media_path):
                        resume_path = media_path
                        print(f'Found resume at media path: {resume_path}')
                except Exception as name_error:
                    print(f"Error with relative path: {str(name_error)}")
            
            if not resume_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    media_path = os.path.join(settings.MEDIA_ROOT, 'applications', 'resumes', filename)
                    
                    if os.path.exists(media_path):
                        resume_path = media_path
                        print(f'Found resume in applications/resumes directory: {resume_path}')
                except Exception as filename_error:
                    print(f"Error with filename in applications/resumes: {str(filename_error)}")
            
            if not resume_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    found = False
                    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                        if filename in files:
                            resume_path = os.path.join(root, filename)
                            print(f'Found resume by filename at: {resume_path}')
                            found = True
                            break
                except Exception as search_error:
                    print(f"Error searching for file: {str(search_error)}")
            
            if not resume_path:
                messages.error(request, 'Resume file could not be found. The candidate may need to upload it again.')
                return redirect('recruiter_dashboard')
            
            if not os.path.exists(resume_path):
                relative_path = str(application.resume).replace('\\', '/')
                media_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                
                if os.path.exists(media_path):
                    resume_path = media_path
                else:
                    filename = os.path.basename(str(application.resume))
                    media_path = os.path.join(settings.MEDIA_ROOT, 'applications', 'resumes', filename)
                    
                    if os.path.exists(media_path):
                        resume_path = media_path
            
            parsed_resume = parse_resume(resume_path)
                          
        except Exception as e:
            messages.error(request, f'Error parsing resume: {str(e)}')
    
    context = {
        'application': application,
        'parsed_resume': parsed_resume,
    }
    
    return render(request, 'recruiter/application_detail.html', context)


class ParseAllResumesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        keyword = request.data.get("keyword", "").strip()
        print(f"Parsing all resumes with keyword filter: {keyword if keyword else 'None'}")
        
        resumes = Resume.objects.all()
        print(f"Found {resumes.count()} total resumes in the system")
        
        if not resumes.exists():
            return Response({"error": "No resumes found in the system"}, status=status.HTTP_404_NOT_FOUND)
        
        parsed = []
        for resume in resumes:
            try:
                if not hasattr(resume, 'file') or not resume.file:
                    print(f"Resume {resume.id} has no file attached")
                    continue
                    
                file_path = resume.file.path
                print(f"Processing resume {resume.id}, file path: {file_path}")
                
                resume_data = parse_resume(file_path)
                if resume_data:
                    parsed.append(resume_data)
                    print(f"Successfully parsed resume {resume.id}")
                else:
                    print(f"Failed to parse resume {resume.id} - no data returned")
            except Exception as e:
                print(f"Error parsing resume {resume.id}: {str(e)}")
        
        if keyword and parsed:
            print(f"Filtering parsed resumes by keyword: {keyword}")
            parsed = filter_by_keyword_ml(parsed, keyword)
            print(f"After filtering, {len(parsed)} resumes remain")
        
        if not parsed:
            return Response({"error": "No matching results found. Try adjusting your search criteria."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ParsedResumeSerializer(parsed, many=True, context={'request': request})
        response_data = serializer.data
        
        metadata = {
            "total_resumes_found": resumes.count(),
            "total_resumes_parsed": len(parsed),
            "keyword_filter_applied": bool(keyword)
        }
        
        if not response_data:
            return Response({
                "error": "No matching results found. Try adjusting your search criteria.",
                "metadata": metadata
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "results": response_data,
            "metadata": metadata
        }, status=status.HTTP_200_OK)


class ParseSelectedResumesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_ids = request.data.get("resume_ids", [])
        keyword = request.data.get("keyword", "").strip()
        
        print(f"Received resume_ids: {resume_ids}, type: {type(resume_ids)}")
        
        if isinstance(resume_ids, str):
            try:
                import json
                resume_ids = json.loads(resume_ids)
                print(f"Converted resume_ids from JSON string: {resume_ids}")
            except json.JSONDecodeError:
                resume_ids = [id.strip() for id in resume_ids.split(',') if id.strip()]
                print(f"Converted resume_ids from comma-separated string: {resume_ids}")
        
        if not isinstance(resume_ids, list):
            resume_ids = [resume_ids]
            
        resume_ids = [int(id) if isinstance(id, str) and id.isdigit() else id for id in resume_ids]
        print(f"Final resume_ids for query: {resume_ids}")
        
        resumes = Resume.objects.filter(id__in=resume_ids)
        print(f"Found {resumes.count()} resumes matching the IDs")
        
        if not resumes.exists():
            return Response({"error": "No resumes found matching the selected IDs"}, status=status.HTTP_404_NOT_FOUND)
        
        parsed = []
        for resume in resumes:
            try:
                if not hasattr(resume, 'file') or not resume.file:
                    print(f"Resume {resume.id} has no file attached")
                    continue
                    
                file_path = resume.file.path
                print(f"Processing resume {resume.id}, file path: {file_path}")
                
                resume_data = parse_resume(file_path)
                if resume_data:
                    parsed.append(resume_data)
                    print(f"Successfully parsed resume {resume.id}")
                else:
                    print(f"Failed to parse resume {resume.id} - no data returned")
            except Exception as e:
                print(f"Error parsing resume {resume.id}: {str(e)}")
        
        if keyword and parsed:
            print(f"Filtering parsed resumes by keyword: {keyword}")
            parsed = filter_by_keyword_ml(parsed, keyword)
            print(f"After filtering, {len(parsed)} resumes remain")
        
        if not parsed:
            return Response({"error": "No matching results found. Try adjusting your search criteria or selecting different resumes."}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ParsedResumeSerializer(parsed, many=True, context={'request': request})
        response_data = serializer.data
        
        metadata = {
            "total_resumes_found": resumes.count(),
            "total_resumes_parsed": len(parsed),
            "keyword_filter_applied": bool(keyword)
        }

        if not response_data:
            return Response({
                "error": "No matching results found. Try adjusting your search criteria or selecting different resumes.",
                "metadata": metadata
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "results": response_data,
            "metadata": metadata
        }, status=status.HTTP_200_OK)


class CandidateJobListView(generics.ListAPIView):

    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')


class RecruiterProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            recruiter = Recruiter.objects.get(user=request.user)
            serializer = RecruiterProfileSerializer(recruiter)
            return Response(serializer.data)
        except Recruiter.DoesNotExist:
            return Response({"detail": "Recruiter profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        try:
            recruiter = Recruiter.objects.get(user=request.user)
            serializer = RecruiterProfileSerializer(recruiter, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Recruiter.DoesNotExist:
            return Response({"detail": "Recruiter profile not found"}, status=status.HTTP_404_NOT_FOUND)


class JobApplicationsView(generics.ListAPIView):

    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        job_id = self.kwargs.get('pk')
        job = Job.objects.filter(id=job_id, recruiter=self.request.user).first()
        if not job:
            return Application.objects.none()
        return Application.objects.filter(job=job)


class AllApplicationsView(generics.ListAPIView):

    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        recruiter_jobs = Job.objects.filter(recruiter=self.request.user).values_list('id', flat=True)
        return Application.objects.filter(job__id__in=recruiter_jobs)


class DeleteAllJobsView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        deleted_count, _ = Job.objects.filter(recruiter=request.user).delete()
        
        return Response({
            "detail": f"Successfully deleted {deleted_count} jobs and their related applications.",
            "count": deleted_count
        }, status=status.HTTP_200_OK)
