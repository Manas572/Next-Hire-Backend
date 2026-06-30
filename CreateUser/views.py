from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import CandidateRegistrationSerializer,RecruiterRegistrationSerializer,EducationSerializer,ProjectSerializer,ExperienceSerializer
from .models import CandidateProfile,RecruiterProfile,Education,Experience,Project
# Create your views here.
class reg_candidate(CreateAPIView):
    serializer_class=CandidateRegistrationSerializer
    queryset=CandidateProfile.objects.all()

class reg_recruiter(CreateAPIView):
    serializer_class=RecruiterRegistrationSerializer
    queryset=RecruiterProfile.objects.all()

class education_register(CreateAPIView):
    queryset=Education.objects.all()
    serializer_class=EducationSerializer
    def perform_create(self, serializer):
        education = Education(candidate=self.request.user.candidate_profile,**serializer.validated_data)
        education.full_clean()
        education.save()


class project_register(CreateAPIView):
    queryset=Project.objects.all()
    serializer_class=ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)

class experience_register(CreateAPIView):
    queryset=Experience.objects.all()
    serializer_class=ExperienceSerializer
    
    def perform_create(self, serializer):
        experience = Experience(candidate=self.request.user.candidate_profile,**serializer.validated_data)
        experience.full_clean()
        experience.save()
    