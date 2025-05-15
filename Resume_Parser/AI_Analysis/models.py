from django.db import models
from Candidate.models import Candidate, Application

class ResumeAnalysis(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='analysis')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resume_analyses')
    

    parsed_skills = models.JSONField(default=dict, help_text='Extracted skills from resume')
    parsed_education = models.JSONField(default=dict, help_text='Extracted education details')
    parsed_experience = models.JSONField(default=dict, help_text='Extracted work experience')
    parsed_projects = models.JSONField(default=dict, help_text='Extracted project details')
    

    skills_score = models.PositiveSmallIntegerField(default=0, help_text='Score for skills match')
    experience_score = models.PositiveSmallIntegerField(default=0, help_text='Score for experience relevance')
    education_score = models.PositiveSmallIntegerField(default=0, help_text='Score for education match')
    overall_score = models.PositiveSmallIntegerField(default=0, help_text='Overall resume score')
    

    strengths = models.TextField(blank=True, help_text='Resume strengths')
    weaknesses = models.TextField(blank=True, help_text='Areas for improvement')
    improvement_suggestions = models.TextField(blank=True, help_text='Suggestions to improve resume')
    

    keyword_matches = models.JSONField(default=dict, help_text='Matched keywords from job description')
    keyword_match_percentage = models.FloatField(default=0.0, help_text='Percentage of keywords matched')
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analysis for {self.candidate.name}'s application to {self.application.job.designation}"

class AnalysisKeyword(models.Model):
    """Model to store important keywords for job matching"""
    analysis = models.ForeignKey(ResumeAnalysis, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('skill', 'Skill'),
        ('experience', 'Experience'),
        ('education', 'Education'),
        ('other', 'Other')
    ])
    weight = models.FloatField(default=1.0, help_text='Importance weight of this keyword')
    found_in_resume = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.keyword} ({self.category})"
