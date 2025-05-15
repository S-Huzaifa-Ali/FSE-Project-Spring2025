from django.db import models
from Users.models import CustomUser

class Recruiter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"

class Job(models.Model):
    recruiter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='jobs', null=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.JSONField(default=list, help_text='List of required skills')
    experience_requirements = models.TextField(blank=True, help_text='Experience requirements')
    education_requirements = models.TextField(blank=True, help_text='Education requirements')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.designation} at {self.company_name}"
