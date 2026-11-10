from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import CandidateRegistrationSerializer,RecruiterRegistrationSerializer,EducationSerializer,ProjectSerializer,ExperienceSerializer,CandidateProfileSerializer,EducationUpdSer,ProjectUpdSer,ExperienceUpdSer,ProjectListSer,ExperienceListSer,EducationListSer,SkillSerializer
from .models import CandidateProfile,RecruiterProfile,Education,Experience,Project,Skill
from rest_framework.generics import RetrieveUpdateAPIView,UpdateAPIView,ListAPIView
from rest_framework.permissions import AllowAny
# Create your views here.
class reg_candidate(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class=CandidateRegistrationSerializer
    queryset=CandidateProfile.objects.all()

class reg_recruiter(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class=RecruiterRegistrationSerializer
    queryset=RecruiterProfile.objects.all()

class education_register(CreateAPIView):
    queryset=Education.objects.all()
    serializer_class=EducationSerializer
    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)
       


class project_register(CreateAPIView):
    queryset=Project.objects.all()
    serializer_class=ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)

class experience_register(CreateAPIView):
    queryset=Experience.objects.all()
    serializer_class=ExperienceSerializer
    
    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)

class CandidateProfileView(RetrieveUpdateAPIView):
    serializer_class = CandidateProfileSerializer
    def get_object(self):
        return self.request.user.candidate_profile
    

class ProjectUpd(UpdateAPIView):
    serializer_class=ProjectUpdSer
    def get_queryset(self):
        return Project.objects.filter(candidate__user=self.request.user)
    
class EducationUpd(UpdateAPIView):
    serializer_class=EducationUpdSer
    def get_queryset(self):
        return Education.objects.filter(candidate__user=self.request.user)
    
class ExperienceUpd(UpdateAPIView):
    serializer_class=ExperienceUpdSer
    def get_queryset(self):
        return Experience.objects.filter(candidate__user=self.request.user)


class ExperienceListView(ListAPIView):
    serializer_class = ExperienceSerializer
    pagination_class=None
    def get_queryset(self):
        return self.request.user.candidate_profile.experiences.all()


class EducationListView(ListAPIView):
    serializer_class = EducationSerializer
    pagination_class=None
    def get_queryset(self):
        return self.request.user.candidate_profile.educations.all()


class ProjectListView(ListAPIView):
    serializer_class = ProjectSerializer
    pagination_class=None
    def get_queryset(self):
        return self.request.user.candidate_profile.projects.all()
    
class skilllist(ListAPIView):
    queryset=Skill.objects.all()
    serializer_class=SkillSerializer
    pagination_class=None

    
