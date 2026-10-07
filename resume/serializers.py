from rest_framework import serializers
from .models import ResumeDetails

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ResumeDetails
        exclude=["candidate"]
        