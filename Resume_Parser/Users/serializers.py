from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from Candidate.models import Candidate
from Recruiter.models import Recruiter

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False)
    age = serializers.IntegerField(required=False)
    qualification = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    designation = serializers.CharField(required=False)
    contact_number = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'user_type', 'company_name', 'designation', 'name', 'age', 'qualification', 'contact_number']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            contact_number=validated_data.get('contact_number', None)
        )

        if user.user_type == 'candidate':
            name = validated_data.get('name') or validated_data.get('username')
            candidate = Candidate.objects.create(
                user=user,
                name=name,
                age=validated_data.get('age'),
                qualification=validated_data.get('qualification')
            )
            user.candidate_profile = candidate
        elif user.user_type == 'recruiter':
            recruiter = Recruiter.objects.create(
                user=user,
                company_name=validated_data.get('company_name')
            )
            if validated_data.get('designation'):
                from Recruiter.models import Job
                Job.objects.create(
                    recruiter=user,
                    designation=validated_data.get('designation'),
                    company_name=validated_data.get('company_name'),
                    description=''
                )
            user.recruiter_profile = recruiter
        
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials.")
