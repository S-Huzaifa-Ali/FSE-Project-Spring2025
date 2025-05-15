from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeAnalysisViewSet

router = DefaultRouter()
router.register(r'analysis', ResumeAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
]