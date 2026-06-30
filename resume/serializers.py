from rest_framework.serializers import serializers
from .models import ResumeDetails

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResumeDetails
        exclude=["candidate"]
        