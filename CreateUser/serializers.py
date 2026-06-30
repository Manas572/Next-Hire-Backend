from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (User,CandidateProfile,RecruiterProfile,Education,Project,Experience)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["role"] = user.role
        token["is_staff"] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "email": self.user.email,
            "role": self.user.role,
            "is_staff": self.user.is_staff,
        }

        return data


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = CandidateProfile
        fields = [
            "email",
            "password",
            "resume_link",
            "portfolio_url",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "Email already registered."}
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=email,
            password=password,
            role=User.Role.CANDIDATE,
        )

        candidate = CandidateProfile.objects.create(
            user=user,
            **validated_data,
        )

        return candidate


class RecruiterRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = RecruiterProfile
        fields = [
            "email",
            "password",
            "company_name",
            "location",
            "company_website",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"error": "Email already registered."}
            )
        return value

    def validate(self, attrs):
        company_name = attrs.get("company_name")
        location = attrs.get("location")

        if RecruiterProfile.objects.filter(
            company_name=company_name,
            location=location,
        ).exists():
            raise serializers.ValidationError(
                {
                    "error": (
                        "A recruiter profile for this company "
                        "at this location already exists."
                    )
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=email,
            password=password,
            role=User.Role.RECRUITER,
        )

        recruiter = RecruiterProfile.objects.create(user=user,**validated_data,)

        return recruiter
    
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Education
        exclude=["candidate"]
    def validate(self, attrs):
        end_date=attrs.get("end_date")
        start_date=attrs.get("start_date")
        if end_date and start_date>end_date:
            raise serializers.ValidationError({"error":"end date is invalid"})
        
        return attrs


  
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model=Project
        exclude=["candidate"]

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Experience
        exclude=["candidate"]
    def validate(self, attrs):
        end_date=attrs.get("end_date")
        start_date=attrs.get("start_date")
        currently_working=attrs.get("currently_working")
        if end_date and start_date and start_date>end_date:
            raise serializers.ValidationError({"error":"end date is invalid"})
        
        if currently_working and end_date:
            raise serializers.ValidationError({"error":"currently worling cannot have end date"})
        return attrs




