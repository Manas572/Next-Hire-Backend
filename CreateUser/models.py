from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        if not password:
            raise ValueError(_('The password must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    username = None 
    email = models.EmailField(_('email address'), unique=True)
    class Role(models.TextChoices):
        CANDIDATE = 'CANDIDATE', 'Candidate'
        RECRUITER = 'RECRUITER', 'Recruiter'

    role = models.CharField(
        max_length=15, 
        choices=Role.choices, 
        default=Role.CANDIDATE,
        db_index=True 
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    objects = CustomUserManager()
    
    def __str__(self):
        if self.is_superuser:
            return f"{self.email} (Admin)"
        return f"{self.email} ({self.get_role_display()})"
    

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
    

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    profile_image = models.URLField(blank=True)
    resume_link = models.URLField(max_length=500, blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    phone_number=models.CharField( max_length=15,null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    codolio_url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    interview_practice_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Candidate: {self.user.email}"
    
class Experience(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="experiences"
    )
    class EmploymentType(models.TextChoices):
        FULL_TIME="FULL_TIME","FULL_TIME"
        INTERN="INTERN","INTERN"
        PART_TIME="PART_TIME","PART_TIME"
        CONTRACT="CONTRACT","CONTRACT"

    company = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    employment_type=models.CharField(max_length=15,choices=EmploymentType.choices)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
         raise ValidationError("End date cannot be before start date.")

        if self.currently_working and self.end_date:
         raise ValidationError({"error":"Current job should not have an end date"})

    def __str__(self):
        return f"{self.designation} at {self.company}"
    
    class Meta:
        ordering = ["-start_date"]
    
class Project(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.ManyToManyField(Skill)
    github_link = models.URLField()
    deployed_link = models.URLField(blank=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Education(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="educations"
    )
    institute = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4,decimal_places=2,blank=True,null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree}-{self.institute}"
    
    def clean(self):
        if self.end_date and self.start_date and self.start_date>self.end_date:
            raise ValidationError({"error":"end date is before start date"})
    
    class Meta:
        ordering = ["-start_date"]

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recruiter_profile')
    company_name = models.CharField(max_length=255, db_index=True)
    location=models.CharField(max_length=100)
    company_website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company_name", "location"],
                name="unique_company_location"
            )
        ]
    
    def __str__(self):
        return f"Recruiter: {self.company_name} ({self.user.email})"