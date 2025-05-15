from django.db import models
from django.conf import settings
from Recruiter.models import Job

class Candidate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_content = models.JSONField(null=True, blank=True)
    skills = models.JSONField(default=list)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    is_parsed = models.BooleanField(default=False)
    last_parsed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Resume for {self.candidate.name} - {self.uploaded_at}"

class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='applications/resumes/')

    def __str__(self):
        return f"{self.candidate.name} -> {self.job.designation}"
