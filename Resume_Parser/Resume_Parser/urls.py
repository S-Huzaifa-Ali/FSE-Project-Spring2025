from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

from Users.views import home_view, signup_view, login_view, logout_view, profile_view
from Candidate.views import candidate_dashboard_view, job_list_view, application_list_view, job_detail_view
from Candidate.resume_views import serve_resume_file
from Recruiter.views import recruiter_dashboard_view, job_management_view, resume_parser_view, application_detail_view, job_edit_view, job_delete_view
from AI_Analysis.views import resume_analysis_view

urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', login_required(profile_view), name='profile'),
    

    path('candidate/dashboard/', login_required(candidate_dashboard_view), name='candidate_dashboard'),
    path('candidate/profile/', login_required(profile_view), name='candidate_profile'),
    path('jobs/', login_required(job_list_view), name='job_list'),
    path('jobs/<int:job_id>/', login_required(job_detail_view), name='job_detail'),
    path('applications/', login_required(application_list_view), name='application_list'),
    

    path('recruiter/dashboard/', login_required(recruiter_dashboard_view), name='recruiter_dashboard'),
    path('recruiter/profile/', login_required(profile_view), name='recruiter_profile'),
    path('jobs/manage/', login_required(job_management_view), name='job_management'),
    path('jobs/edit/<int:job_id>/', login_required(job_edit_view), name='job_edit'),
    path('jobs/delete/<int:job_id>/', login_required(job_delete_view), name='job_delete'),
    path('resume/parse/', login_required(resume_parser_view), name='resume_parser'),
    path('applications/<int:application_id>/', login_required(application_detail_view), name='application_detail'),
    path('resume/analysis/<int:application_id>/', login_required(resume_analysis_view), name='resume_analysis'),
    

    path('resume/download/<int:application_id>/', login_required(serve_resume_file), name='serve_resume_file'),
    

    path('api/AI/', include('AI_Analysis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from django.views.static import serve
    urlpatterns += [
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
