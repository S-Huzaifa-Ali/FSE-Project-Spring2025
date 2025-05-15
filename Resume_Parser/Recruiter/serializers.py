from rest_framework import serializers
from .models import Job, Recruiter
from Candidate.models import Application, Candidate

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['recruiter']

class RecruiterProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    contact_number = serializers.CharField(source='user.contact_number', required=False)
    designation = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Recruiter
        fields = ['email', 'name', 'company_name', 'industry', 'company_description', 
                  'contact_email', 'contact_phone', 'contact_number', 'designation']
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'contact_number' in user_data and user_data['contact_number']:
            instance.user.contact_number = user_data['contact_number']
            instance.user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    job_title = serializers.CharField(source='job.designation', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    applied_at = serializers.DateTimeField(read_only=True)
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = ['id', 'job', 'job_title', 'company_name', 'candidate', 'candidate_name', 
                 'resume', 'resume_url', 'applied_at']
        read_only_fields = ['id', 'job', 'candidate', 'resume', 'applied_at']
    
    def get_resume_url(self, obj):
        if obj.resume and hasattr(obj.resume, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.resume.url)
            return obj.resume.url
        return None
