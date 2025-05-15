from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .serializers import UserSignupSerializer
from django.views.decorators.csrf import csrf_protect
from Candidate.models import Candidate
from Recruiter.models import Recruiter

def home_view(request):
    return render(request, 'home.html')

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'signup.html')
        
        data = {
            'username': username,
            'email': email,
            'password': password1,
            'user_type': user_type
        }
        
        serializer = UserSignupSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            if user.user_type == 'candidate':
                if not hasattr(user, 'candidate'):
                    Candidate.objects.create(user=user, name=username)
            elif user.user_type == 'recruiter':
                if not hasattr(user, 'recruiter'):
                    Recruiter.objects.create(user=user, company_name='Company Name')
            
            login(request, user)
            
            if user.user_type == 'candidate':
                return redirect('candidate_dashboard')
            else:
                return redirect('recruiter_dashboard')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return render(request, 'signup.html')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.user_type == user_type:
                login(request, user)
                
                if user.user_type == 'candidate':
                    return redirect('candidate_dashboard')
                else:
                    return redirect('recruiter_dashboard')
            else:
                messages.error(request, 'Invalid user type selected')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    
    profile = None
    if user.user_type == 'candidate':
        try:
            profile = Candidate.objects.get(user=user)
        except Candidate.DoesNotExist:
            profile = Candidate.objects.create(user=user, name=user.username)
    elif user.user_type == 'recruiter':
        try:
            profile = Recruiter.objects.get(user=user)
        except Recruiter.DoesNotExist:
            profile = Recruiter.objects.create(user=user, company_name='Company Name')
    
    if request.method == 'POST':
        if user.user_type == 'candidate':
            profile.name = request.POST.get('name', profile.name)
            profile.phone = request.POST.get('phone', profile.phone)
            profile.qualification = request.POST.get('qualification', profile.qualification)
            profile.skills = request.POST.get('skills', profile.skills)
            profile.experience = request.POST.get('experience', profile.experience)
            profile.education = request.POST.get('education', profile.education)
            
            user.email = request.POST.get('email', user.email)
            user.save()
                
            profile.save()
            messages.success(request, 'Profile updated successfully')
        
        elif user.user_type == 'recruiter':
            profile.company_name = request.POST.get('company_name', profile.company_name)
            profile.designation = request.POST.get('designation', profile.designation)
            profile.company_description = request.POST.get('company_description', profile.company_description)
            
            user.email = request.POST.get('email', user.email)
            user.save()
            
            profile.save()
            messages.success(request, 'Profile updated successfully')
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'profile.html', context)
