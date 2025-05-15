from rest_framework import serializers
from .models import ResumeAnalysis, AnalysisKeyword
from Candidate.models import Application


class ParsedResumeSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    relevant_skills = serializers.ListField(child=serializers.CharField(), required=False)
    education = serializers.DictField(required=False, allow_null=True)
    experience = serializers.DictField(required=False, allow_null=True)
    projects = serializers.DictField(required=False, allow_null=True)
    qualification = serializers.CharField(required=False, allow_null=True)
    match_score = serializers.IntegerField(required=False, default=0)
    resume_url = serializers.SerializerMethodField(required=False)
    
    def get_resume_url(self, obj):
        if isinstance(obj, dict) and obj.get('resume_path'):
            request = self.context.get('request')
            path = obj['resume_path']
            
            path = path.replace('\\', '/')
            
            if '/' in path:
                if 'media/' in path:
                    parts = path.split('media/')
                    if len(parts) > 1:
                        path = parts[-1]
                else:
                    path = path.split('/')[-1]
            
            if not path.startswith('media/') and not path.startswith('/media/'):
                path = f'media/{path}'
            elif path.startswith('/media/'):
                path = path[1:]
            
            path = path.replace('//', '/')
                
            if request is not None:
                return request.build_absolute_uri(f'/{path}')
            return f'/{path}'
        return None

class AnalysisKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisKeyword
        fields = ['keyword', 'category', 'weight', 'found_in_resume']

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    keywords = AnalysisKeywordSerializer(many=True, read_only=True)
    
    class Meta:
        model = ResumeAnalysis
        fields = [
            'id', 'application', 'candidate',
            'parsed_skills', 'parsed_education', 'parsed_experience', 'parsed_projects',
            'skills_score', 'experience_score', 'education_score', 'overall_score',
            'strengths', 'weaknesses', 'improvement_suggestions',
            'keyword_matches', 'keyword_match_percentage',
            'keywords', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        analysis = ResumeAnalysis.objects.create(**validated_data)
        
        application = validated_data.get('application')
        if application and application.job:
            job = application.job
            for skill in job.required_skills:
                AnalysisKeyword.objects.create(
                    analysis=analysis,
                    keyword=skill,
                    category='skill',
                    weight=1.0
                )
            
            if job.experience_requirements:
                AnalysisKeyword.objects.create(
                    analysis=analysis,
                    keyword=job.experience_requirements,
                    category='experience',
                    weight=1.0
                )
            
            if job.education_requirements:
                AnalysisKeyword.objects.create(
                    analysis=analysis,
                    keyword=job.education_requirements,
                    category='education',
                    weight=1.0
                )
        
        return analysis
