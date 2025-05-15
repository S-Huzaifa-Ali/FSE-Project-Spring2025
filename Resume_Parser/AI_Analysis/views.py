from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ResumeAnalysis
from .serializers import ResumeAnalysisSerializer
from .utils import parse_resume
from Candidate.models import Application
import re
import os
import openai

class ResumeAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ResumeAnalysis.objects.all()
    serializer_class = ResumeAnalysisSerializer
    
    def get_serializer_context(self):
        context = {
            'request': getattr(self, 'request', None),
            'format': getattr(self, 'format_kwarg', None),
            'view': self
        }
        return context

    def create(self, request, *args, **kwargs):
        application_id = kwargs.get('application') or request.data.get('application')
        
        if not application_id:
            return Response({'error': 'Application ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Received application ID: {application_id}, type: {type(application_id)}")
        
        if isinstance(application_id, str) and application_id.isdigit():
            application_id = int(application_id)
            print(f"Converted application ID to integer: {application_id}")
            
        try:
            from Candidate.models import Application
            application = Application.objects.get(id=application_id)
            print(f"Found application: {application.id} for candidate: {application.candidate.name}")
        except (Application.DoesNotExist, ValueError, TypeError) as e:
            print(f"Application validation error: {str(e)}, application_id: {application_id}, type: {type(application_id)}")
            return Response({'error': 'Please select an existing application'}, status=status.HTTP_400_BAD_REQUEST)
            
        if not hasattr(application, 'resume') or not application.resume:
            print(f"Error: Application {application.id} has no resume attached")
            return Response({'error': 'Resume file is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Resume file found: {application.resume.name}")
            
        resume_path = None
        try:
            try:
                if hasattr(application.resume, 'path'):
                    absolute_path = application.resume.path
                    if os.path.exists(absolute_path):
                        resume_path = absolute_path
                        print(f'Found resume at absolute path: {resume_path}')
            except Exception as path_error:
                print(f"Error accessing absolute path: {str(path_error)}")
            
            if not resume_path:
                try:
                    relative_path = str(application.resume.name).replace('\\', '/')
                    if relative_path.startswith('media/'):
                        relative_path = relative_path[6:]
                    media_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    
                    if os.path.exists(media_path):
                        resume_path = media_path
                        print(f'Found resume at media path: {resume_path}')
                except Exception as name_error:
                    print(f"Error with relative path: {str(name_error)}")
            
            if not resume_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    media_path = os.path.join(settings.MEDIA_ROOT, 'applications', 'resumes', filename)
                    
                    if os.path.exists(media_path):
                        resume_path = media_path
                        print(f'Found resume in applications/resumes directory: {resume_path}')
                except Exception as filename_error:
                    print(f"Error with filename in applications/resumes: {str(filename_error)}")
            
            if not resume_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    media_file_path = os.path.join(settings.MEDIA_ROOT, filename)
                    if os.path.exists(media_file_path):
                        resume_path = media_file_path
                        print(f'Found resume in media root: {resume_path}')
                except Exception as root_error:
                    print(f"Error checking media root: {str(root_error)}")
            
            if not resume_path:
                try:
                    filename = os.path.basename(str(application.resume.name))
                    found = False
                    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                        if filename in files:
                            resume_path = os.path.join(root, filename)
                            print(f'Found resume by filename at: {resume_path}')
                            found = True
                            break
                    
                    if not found:
                        print(f'Warning: Resume file not found anywhere')
                        return Response({'error': 'Unable to locate your resume file. Please try uploading it again or contact support.'}, 
                                        status=status.HTTP_404_NOT_FOUND)
                except Exception as search_error:
                    print(f"Error searching for file: {str(search_error)}")
            
            if not resume_path:
                return Response({'error': 'Resume file could not be found. Please try uploading it again.'}, 
                                status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(f'Error accessing resume file: {str(e)}')
            return Response({'error': f'Error accessing resume file: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                resume_path = application.resume.name
                print(f'Using relative path as fallback: {resume_path}')
                
                if not os.path.exists(resume_path):
                    file_name = os.path.basename(resume_path)
                    media_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    if os.path.exists(media_file_path):
                        resume_path = media_file_path
                        print(f'Found resume using filename fallback: {resume_path}')
            except Exception as inner_e:
                print(f'Error getting resume name: {str(inner_e)}')
                return Response({'error': f'Cannot access resume file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        parsed_data = parse_resume(resume_path)

        analysis_data = {
            'application': application.id,
            'candidate': application.candidate.id,
            'parsed_skills': parsed_data.get('skills', []),
            'parsed_education': parsed_data.get('education', {}),
            'parsed_experience': parsed_data.get('experience', {}),
            'parsed_projects': parsed_data.get('projects', {})
        }

        serializer = self.get_serializer(data=analysis_data)
        serializer.is_valid(raise_exception=True)
        analysis = serializer.save()

        self._analyze_with_openai(analysis, application)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _analyze_with_openai(self, analysis, application):
        if not application:
            print("Error: Application object is None")
            analysis.strengths = "Error: Could not find the application data. Please try again or contact support."
            analysis.save()
            return
            
        if not hasattr(application, 'job') or not application.job:
            print("Error: Application has no associated job")
            analysis.strengths = "Error: This application has no associated job posting. Please ensure the job posting exists."
            analysis.save()
            return
            
        if not settings.OPENAI_API_KEY:
            print("Error: OpenAI API key is not configured")
            analysis.strengths = "Error: OpenAI API key is not configured properly. Please contact support."
            analysis.save()
            return
            
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            analysis.strengths = f"Error initializing OpenAI API: {str(e)}"
            analysis.save()
            return

        prompt = f"""Analyze this resume for the {application.job.designation} position:
        Skills: {analysis.parsed_skills}
        Education: {analysis.parsed_education}
        Experience: {analysis.parsed_experience}
        Projects: {analysis.parsed_projects}

        Job Requirements:
        Required Skills: {application.job.required_skills}
        Experience: {application.job.experience_requirements}
        Education: {application.job.education_requirements}

        Please provide:
        1. Skills match score (0-100)
        2. Experience relevance score (0-100)
        3. Education match score (0-100)
        4. Overall score (0-100)
        5. Strengths
        6. Weaknesses
        7. Improvement suggestions"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume analyzer."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content
            print(f"OpenAI response received: {len(result)} characters")
            
            scores = {
                'skills': re.search(r'Skills match score.*?([0-9]+)', result) or re.search(r'Skills.*?score.*?([0-9]+)', result) or re.search(r'Skills.*?([0-9]+)/100', result),
                'experience': re.search(r'Experience relevance score.*?([0-9]+)', result) or re.search(r'Experience.*?score.*?([0-9]+)', result) or re.search(r'Experience.*?([0-9]+)/100', result),
                'education': re.search(r'Education match score.*?([0-9]+)', result) or re.search(r'Education.*?score.*?([0-9]+)', result) or re.search(r'Education.*?([0-9]+)/100', result),
                'overall': re.search(r'Overall score.*?([0-9]+)', result) or re.search(r'Overall.*?score.*?([0-9]+)', result) or re.search(r'Overall.*?([0-9]+)/100', result)
            }
            
            try:
                analysis.skills_score = int(scores['skills'].group(1)) if scores['skills'] else 0
            except (AttributeError, ValueError):
                print("Failed to extract skills score")
                analysis.skills_score = 0
                
            try:
                analysis.experience_score = int(scores['experience'].group(1)) if scores['experience'] else 0
            except (AttributeError, ValueError):
                print("Failed to extract experience score")
                analysis.experience_score = 0
                
            try:
                analysis.education_score = int(scores['education'].group(1)) if scores['education'] else 0
            except (AttributeError, ValueError):
                print("Failed to extract education score")
                analysis.education_score = 0
                
            try:
                analysis.overall_score = int(scores['overall'].group(1)) if scores['overall'] else 0
            except (AttributeError, ValueError):
                print("Failed to extract overall score")
                analysis.overall_score = 0
                
            try:
                strengths_match = re.search(r'(?:Strengths|Strength|Pros|Positives):?\s*(.+?)(?=\n\s*(?:Weaknesses|Weakness|Cons|Areas|Improvement|$))', result, re.DOTALL)
                weaknesses_match = re.search(r'(?:Weaknesses|Weakness|Cons|Areas for improvement):?\s*(.+?)(?=\n\s*(?:Improvement suggestions|Suggestions|Recommendations|$))', result, re.DOTALL)
                suggestions_match = re.search(r'(?:Improvement suggestions|Suggestions|Recommendations):?\s*(.+?)(?=\n|$)', result, re.DOTALL)
                
                try:
                    analysis.strengths = strengths_match.group(1).strip() if strengths_match else 'No strengths identified.'
                except (AttributeError, IndexError):
                    analysis.strengths = 'Error extracting strengths from analysis.'
                    
                try:
                    analysis.weaknesses = weaknesses_match.group(1).strip() if weaknesses_match else 'No weaknesses identified.'
                except (AttributeError, IndexError):
                    analysis.weaknesses = 'Error extracting weaknesses from analysis.'
                    
                try:
                    analysis.improvement_suggestions = suggestions_match.group(1).strip() if suggestions_match else 'No improvement suggestions provided.'
                except (AttributeError, IndexError):
                    analysis.improvement_suggestions = 'Error extracting improvement suggestions from analysis.'
            except Exception as e:
                print(f"Error extracting feedback sections: {str(e)}")
                analysis.strengths = 'Error processing resume analysis.'
                analysis.weaknesses = 'Please try again or contact support.'
                analysis.improvement_suggestions = f'Technical error: {str(e)}'
            
            try:
                job_keywords = set()
                if hasattr(application, 'job') and application.job and hasattr(application.job, 'required_skills'):
                    if isinstance(application.job.required_skills, list):
                        job_keywords = set(skill.lower() for skill in application.job.required_skills if skill)
                    elif isinstance(application.job.required_skills, str):
                        job_keywords = set(skill.lower().strip() for skill in application.job.required_skills.split(',') if skill.strip())
                    else:
                        print(f"Warning: Unexpected type for job required_skills: {type(application.job.required_skills)}")
                        try:
                            skills_str = str(application.job.required_skills)
                            job_keywords = set(skill.lower().strip() for skill in skills_str.split(',') if skill.strip())
                        except:
                            pass
                else:
                    print("Warning: Application has no job or job has no required_skills")
                
                resume_keywords = set()
                if hasattr(analysis, 'parsed_skills'):
                    if isinstance(analysis.parsed_skills, list):
                        resume_keywords = set(skill.lower() for skill in analysis.parsed_skills if skill)
                    elif isinstance(analysis.parsed_skills, dict):
                        resume_keywords = set(skill.lower() for skill in analysis.parsed_skills.keys() if skill)
                    elif isinstance(analysis.parsed_skills, str):
                        resume_keywords = set(skill.lower().strip() for skill in analysis.parsed_skills.split(',') if skill.strip())
                    else:
                        print(f"Warning: Unexpected type for parsed_skills: {type(analysis.parsed_skills)}")
                else:
                    print("Warning: Analysis has no parsed_skills attribute")
                
                matched_keywords = job_keywords.intersection(resume_keywords)
                
                analysis.keyword_matches = list(matched_keywords)
                analysis.keyword_match_percentage = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0
            except Exception as e:
                print(f"Error calculating keyword matches: {str(e)}")
                analysis.keyword_matches = []
                analysis.keyword_match_percentage = 0
            
            analysis.save()
            
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            analysis.strengths = f"Error analyzing resume with OpenAI: {str(e)}"
            analysis.save()
            return

    @action(detail=True, methods=['post'])
    def reanalyze(self, request, pk=None):
        analysis = self.get_object()
        
        if not hasattr(analysis, 'application') or not analysis.application:
            return Response(
                {'error': 'This analysis has no associated application'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        application = analysis.application
        
        if not application.resume:
            return Response(
                {'error': 'The application has no resume attached'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        self._analyze_with_openai(analysis, application)
        
        return Response(self.get_serializer(analysis).data)


@login_required
def resume_analysis_view(request, application_id):
    """View for displaying resume analysis results"""
    application = get_object_or_404(Application, id=application_id)
    
    if request.user.user_type == 'candidate':
        if application.candidate.user != request.user:
            messages.error(request, 'Access denied. This is not your application.')
            return redirect('candidate_dashboard')
    elif request.user.user_type == 'recruiter':
        if application.job.recruiter != request.user:
            messages.error(request, 'Access denied. This application is not for your job.')
            return redirect('recruiter_dashboard')
    else:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        analysis = ResumeAnalysis.objects.get(application=application)
    except ResumeAnalysis.DoesNotExist:
        if request.method == 'POST':
            viewset = ResumeAnalysisViewSet()
            viewset.request = request
            viewset.format_kwarg = None
            response = viewset.create(request, application=application_id)
            
            if response.status_code == 201:
                analysis_id = response.data.get('id')
                analysis = ResumeAnalysis.objects.get(id=analysis_id)
                messages.success(request, 'Resume analysis completed successfully.')
            else:
                error_message = response.data.get('error', 'Failed to analyze resume.')
                messages.error(request, error_message)
                if request.user.user_type == 'candidate':
                    return redirect('application_list')
                else:
                    return redirect('recruiter_dashboard')
        else:
            template = 'candidate/resume_analysis_create.html' if request.user.user_type == 'candidate' else 'recruiter/resume_analysis_create.html'
            return render(request, template, {
                'application': application
            })
    
    context = {
        'application': application,
        'analysis': {
            'skills': analysis.parsed_skills,
            'experience': analysis.parsed_experience,
            'education': analysis.parsed_education,
            'summary': analysis.parsed_projects,
            'skills_score': analysis.skills_score,
            'experience_score': analysis.experience_score,
            'education_score': analysis.education_score,
            'overall_score': analysis.overall_score,
            'strengths': analysis.strengths,
            'weaknesses': analysis.weaknesses,
            'improvement_suggestions': analysis.improvement_suggestions,
            'keyword_matches': analysis.keyword_matches,
            'keyword_match_percentage': analysis.keyword_match_percentage
        }
    }
    
    template = 'candidate/resume_analysis.html' if request.user.user_type == 'candidate' else 'recruiter/resume_analysis.html'
    return render(request, template, context)
