from django.shortcuts import render
from jobposting.models import Job,Application
from django.db.models.functions import TruncDate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
# Create your views here.

@api_view(['GET'])
def job_count(request,recruiter_id):
    counts=(Job.objects.filter(recruiter=recruiter_id)).count()
    return Response({"counts":counts})

@api_view(['GET'])
#@permission_classes([AllowAny])
def app_count(request, recruiter_id):
    counts = Application.objects.filter(job__recruiter=recruiter_id).count()
    return Response({'counts': counts})


