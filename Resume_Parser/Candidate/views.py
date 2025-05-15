from rest_framework import generics, permissions
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Recruiter.models import Job
from .models import Candidate, Application, Resume
from .serializers import CandidateProfileSerializer, JobSerializer, ApplicationSerializer

class CandidateProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Candidate.objects.get(user=self.request.user)

class JobListView(generics.ListAPIView):

    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

class JobApplyView(generics.CreateAPIView):

    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        response.data['message'] = "Your application has been successfully submitted."
        
        return response

class ApplicationListView(generics.ListAPIView):

    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        candidate = Candidate.objects.get(user=self.request.user)
        return Application.objects.filter(candidate=candidate)

@login_required
def candidate_dashboard_view(request):

    if request.user.user_type != 'candidate':
        messages.error(request, 'Access denied. You are not a candidate.')
        return redirect('home')
    
    try:
        candidate = Candidate.objects.get(user=request.user)
    except Candidate.DoesNotExist:
        candidate = Candidate.objects.create(user=request.user, name=request.user.username)
    
    recent_jobs = Job.objects.all().order_by('-created_at')[:5]
    
    applications = Application.objects.filter(candidate=candidate).order_by('-applied_at')
    
    context = {
        'candidate': candidate,
        'recent_jobs': recent_jobs,
        'applications': applications,
    }
    
    return render(request, 'candidate/dashboard.html', context)

@login_required
def job_list_view(request):

    if request.user.user_type != 'candidate':
        messages.error(request, 'Access denied. You are not a candidate.')
        return redirect('home')
    
    jobs = Job.objects.all().order_by('-created_at')
    
    candidate = Candidate.objects.get(user=request.user)
    
    applied_job_ids = Application.objects.filter(candidate=candidate).values_list('job_id', flat=True)
    
    context = {
        'jobs': jobs,
        'applied_job_ids': applied_job_ids,
    }
    
    return render(request, 'candidate/job_list.html', context)

@login_required
def job_detail_view(request, job_id):

    if request.user.user_type != 'candidate':
        messages.error(request, 'Access denied. You are not a candidate.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id)
    
    candidate = Candidate.objects.get(user=request.user)
    
    already_applied = Application.objects.filter(candidate=candidate, job=job).exists()
    
    if request.method == 'POST' and not already_applied:
        if 'resume' in request.FILES:
            resume_file = request.FILES['resume']
            
            application = Application.objects.create(
                candidate=candidate,
                job=job,
                resume=resume_file
            )
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('application_list')
        else:
            messages.error(request, 'Please upload your resume')
    
    context = {
        'job': job,
        'already_applied': already_applied,
    }
    
    return render(request, 'candidate/job_detail.html', context)

@login_required
def application_list_view(request):

    if request.user.user_type != 'candidate':
        messages.error(request, 'Access denied. You are not a candidate.')
        return redirect('home')
    
    candidate = Candidate.objects.get(user=request.user)
    
    applications = Application.objects.filter(candidate=candidate).order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    
    return render(request, 'candidate/application_list.html', context)
