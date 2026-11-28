from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ResumeDetails
from .serializers import (
    PublicResumeSerializer,
    ResumeListSerializer,
    ResumeSerializer,
)


class ResumeListCreateView(ListCreateAPIView):
    def get_queryset(self):
        return ResumeDetails.objects.filter(candidate=self.request.user.candidate_profile)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ResumeListSerializer
        return ResumeSerializer

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user.candidate_profile)


class ResumeOwnerDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    def get_queryset(self):
        return ResumeDetails.objects.filter(candidate=self.request.user.candidate_profile)


class PublicResumeView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicResumeSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            ResumeDetails.objects.filter(public=True)
            .select_related("candidate__user")
            .prefetch_related(
                "included_experiences",
                "included_projects",
                "included_educations",
                "included_skills",
            )
        )