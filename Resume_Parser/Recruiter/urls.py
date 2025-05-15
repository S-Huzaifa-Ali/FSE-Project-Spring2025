from django.urls import path
from .views import (
    JobListCreateView,
    JobRetrieveUpdateDestroyView,
    ParseAllResumesView,
    ParseSelectedResumesView,
    CandidateJobListView,
    RecruiterProfileView,
    JobApplicationsView,
    AllApplicationsView,
    DeleteAllJobsView,
)

urlpatterns = [
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
    path('jobs/<int:pk>/applications/', JobApplicationsView.as_view(), name='job-applications'),
    path('applications/', AllApplicationsView.as_view(), name='all-applications'),


    path('parse/all/', ParseAllResumesView.as_view(), name='parse-all-resumes'),
    path('parse/selected/', ParseSelectedResumesView.as_view(), name='parse-selected-resumes'),

    path('parse-all/', ParseAllResumesView.as_view(), name='parse-all-resumes-hyphen'),
    path('parse-selected/', ParseSelectedResumesView.as_view(), name='parse-selected-resumes-hyphen'),

    path('parse_all/', ParseAllResumesView.as_view(), name='parse-all-resumes-underscore'),
    path('parse_selected/', ParseSelectedResumesView.as_view(), name='parse-selected-resumes-underscore'),
    

    path('profile/', RecruiterProfileView.as_view(), name='recruiter-profile'),
]

urlpatterns += [
    path('jobs/all/', CandidateJobListView.as_view(), name='job-list-all'),
]
