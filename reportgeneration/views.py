from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from jobposting.models import Job
from .serializers import AnalysisSerializer


class ReportGeneration(CreateAPIView):
    serializer_class = AnalysisSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["job"] = get_object_or_404(
            Job,
            pk=self.kwargs["pk"]
        )
        return context