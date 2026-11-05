from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .models import ResumeDetails
from .serializers import ResumeSerializer
# Create your views here.

class resume_register(CreateAPIView):
    queryset=ResumeDetails.objects.all()
    serializer_class=ResumeSerializer
    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)


