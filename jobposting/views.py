from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from .models import Job
from .serializers import JobSerializer,JobApplySerializer,Listing
from django.shortcuts import get_object_or_404
# Create your views here.
class CreateJob(CreateAPIView):
    serializer_class = JobSerializer
    queryset = Job.objects.all()

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user.recruiter_profile)

class ApplyJob(CreateAPIView):
    serializer_class = JobApplySerializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = get_object_or_404(Job,pk=self.kwargs["pk"])

        return context
    
    def perform_create(self, serializer):
        job = get_object_or_404(Job,pk=self.kwargs["pk"])
        serializer.save(candidate=self.request.user.candidate_profile,job=job)

class ListAlljob(ListAPIView):
    queryset=Job.objects.filter(is_active=True).order_by("-created_at")
    serializer_class=Listing

class JobDetail(RetrieveAPIView):
    queryset=Job.objects.filter(is_active=True).select_related("recruiter")
    serializer_class=Listing
