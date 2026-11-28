from rest_framework import serializers
from .models import ResumeDetails

from CreateUser.serializers import (
    EducationSerializer,
    ExperienceSerializer,
    ProjectSerializer,
    SkillSerializer,
)
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeDetails
        exclude = ["candidate"]
        read_only_fields = ["slug"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            profile = request.user.candidate_profile
            self.fields["included_experiences"].queryset = profile.experiences.all()
            self.fields["included_projects"].queryset = profile.projects.all()
            self.fields["included_educations"].queryset = profile.educations.all()
            self.fields["included_skills"].queryset = profile.skills.all()

class _PersonalInfoSerializer(serializers.Serializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source="candidate.phone_number", allow_null=True)
    linkedin_url = serializers.URLField(source="candidate.linkedin_url", allow_null=True)
    github_url = serializers.URLField(source="candidate.github_url", allow_null=True)
    portfolio_url = serializers.URLField(source="candidate.portfolio_url", allow_null=True)
    profile_image = serializers.URLField(source="candidate.profile_image", allow_blank=True)

    def get_full_name(self, obj):
        return obj.candidate.user.get_full_name() or obj.candidate.user.username

    def get_email(self, obj):
        return obj.candidate.user.email


class PublicResumeSerializer(serializers.ModelSerializer):
    personal_info = serializers.SerializerMethodField()
    included_educations = EducationSerializer(many=True, read_only=True)
    included_experiences = ExperienceSerializer(many=True, read_only=True)
    included_projects = ProjectSerializer(many=True, read_only=True)
    included_skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = ResumeDetails
        fields = [
            "id",
            "slug",
            "title",
            "template",
            "accent_color",
            "professional_summary",
            "public",
            "personal_info",
            "included_educations",
            "included_experiences",
            "included_projects",
            "included_skills",
        ]

    def get_personal_info(self, obj):
        return _PersonalInfoSerializer(obj).data


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeDetails
        fields = ["id", "slug", "title", "template", "accent_color", "public"]