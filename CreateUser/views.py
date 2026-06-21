from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import CandidateRegistrationSerializer,RecruiterRegistrationSerializer
from .models import CandidateProfile,RecruiterProfile
# Create your views here.
class reg_candidate(CreateAPIView):
    serializer_class=CandidateRegistrationSerializer
    queryset=CandidateProfile.objects.all()

class reg_recruiter(CreateAPIView):
    serializer_class=RecruiterRegistrationSerializer
    queryset=RecruiterProfile.objects.all()