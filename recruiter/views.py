from django.shortcuts import render
from jobposting.models import Job,Application
from django.db.models.functions import TruncDate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count
from CreateUser.permissions import IsAuthenticatedRecruiter
# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticatedRecruiter])
def job_count(request,recruiter_id):
    counts=(Job.objects.filter(recruiter__user=request.user, recruiter_id=recruiter_id)).count()
    return Response({"counts":counts})

@api_view(['GET'])
@permission_classes([IsAuthenticatedRecruiter])
def app_count(request, recruiter_id):
    counts = Application.objects.filter(job__recruiter__user=request.user, job__recruiter_id=recruiter_id).count()
    return Response({'counts': counts})


@api_view(['GET'])
@permission_classes([IsAuthenticatedRecruiter])
def recruiter_applications(request, recruiter_id):
    jobs = Job.objects.filter(recruiter__user=request.user, recruiter_id=recruiter_id).annotate(application_count=Count('applications')).order_by('-created_at')
    data = []
    for job in jobs:
        data.append({'job_id': job.id,'title': job.title,'application_count': job.application_count,})

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticatedRecruiter])
def application_details(request, recruiter_id):
    applications = (
        Application.objects
        .filter(job__recruiter__user=request.user, job__recruiter_id=recruiter_id)
        .select_related('job', 'candidate__user')
        .order_by('-applied_at')
    )
    data = []
    for app in applications:
        data.append({
            'job_title': app.job.title,
            'candidate_email': app.candidate.user.email,
            'resume_link': app.resume_link,
            'portfolio_url': app.portfolio_url,
            'linkedin_url': app.linkedin_url,
            'github_url': app.github_url,
            'codolio_url': app.codolio_url,
            'status': app.statustype,
            'applied_at': app.applied_at,
        })

    return Response(data)
