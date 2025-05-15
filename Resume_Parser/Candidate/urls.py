from django.urls import path
from .views import CandidateProfileView, JobListView, JobApplyView, ApplicationListView
from .resume_views import serve_resume_file

urlpatterns = [
    path('profile/', CandidateProfileView.as_view(), name='candidate-profile'),
    path('jobs/', JobListView.as_view(), name='candidate-job-list'),
    path('apply/', JobApplyView.as_view(), name='candidate-job-apply'),
    path('applications/', ApplicationListView.as_view(), name='candidate-applications'),
    path('resume/<int:application_id>/', serve_resume_file, name='candidate-resume-view'),
]
