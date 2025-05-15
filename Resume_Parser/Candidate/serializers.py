from rest_framework import serializers
from .models import Candidate, Application
from Recruiter.models import Job

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['name', 'age', 'qualification', 'resume']

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'designation', 'description', 'company_name', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.designation', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    applied_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'company_name', 'resume', 'applied_at']
        read_only_fields = ['id', 'applied_at', 'job_title', 'company_name']

    def validate_job(self, value):
        if not Job.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Job not found.")
        
        request = self.context['request']
        candidate = Candidate.objects.get(user=request.user)
        if Application.objects.filter(candidate=candidate, job=value).exists():
            raise serializers.ValidationError("You have already applied for this job.")
            
        return value
        
    def validate_resume(self, value):
        file_name = value.name.lower()
        if not (file_name.endswith('.pdf') or file_name.endswith('.docx') or file_name.endswith('.doc')):
            raise serializers.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        candidate = Candidate.objects.get(user=request.user)
        return Application.objects.create(
            candidate=candidate,
            job=validated_data['job'],
            resume=validated_data['resume']
        )
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(representation['job'], dict) and 'id' in representation['job']:
            representation['job'] = representation['job']['id']
        return representation
