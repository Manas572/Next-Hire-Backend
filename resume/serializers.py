from rest_framework import serializers
from .models import ResumeDetails

# Reuse existing serializers from CreateUser — no duplication needed
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


# ── Lightweight personal info (safe fields only) ──────────────────────────────
class _PersonalInfoSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source="candidate.phone_number", allow_null=True)
    linkedin_url = serializers.URLField(source="candidate.linkedin_url", allow_null=True)
    github_url = serializers.URLField(source="candidate.github_url", allow_null=True)
    portfolio_url = serializers.URLField(source="candidate.portfolio_url", allow_null=True)
    profile_image = serializers.URLField(source="candidate.profile_image", allow_blank=True)

    def get_email(self, obj):
        return obj.candidate.user.email


# ── Full read-only serializer for the public live-link view ──────────────────
class PublicResumeSerializer(serializers.ModelSerializer):
    personal_info = serializers.SerializerMethodField()
    included_educations = EducationSerializer(many=True)
    included_experiences = ExperienceSerializer(many=True)
    included_projects = ProjectSerializer(many=True)
    included_skills = SkillSerializer(many=True)

    class Meta:
        model = ResumeDetails
        fields = [
            "id",
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


# ── Lightweight list serializer for the dashboard ─────────────────────────────
class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeDetails
        fields = ["id", "title", "template", "accent_color", "public"]