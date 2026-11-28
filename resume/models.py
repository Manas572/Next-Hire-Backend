import uuid
from django.db import models
from django.utils.text import slugify


class ResumeDetails(models.Model):
    class Template(models.TextChoices):
        CLASSIC = "classic", "Classic"
        MODERN = "modern", "Modern"
        MINIMAL = "minimal", "Minimal"

    candidate = models.ForeignKey(
        "CreateUser.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    title = models.CharField(max_length=100, default="Untitled Resume")
    slug = models.SlugField(unique=True, max_length=120, blank=True)
    public = models.BooleanField(default=False)
    template = models.CharField(max_length=20, choices=Template.choices, default=Template.CLASSIC)
    accent_color = models.CharField(max_length=20, default="#3B82F6")
    professional_summary = models.TextField(default="", blank=True)
    included_experiences = models.ManyToManyField("CreateUser.Experience", blank=True)
    included_projects = models.ManyToManyField("CreateUser.Project", blank=True)
    included_educations = models.ManyToManyField("CreateUser.Education", blank=True)
    included_skills = models.ManyToManyField("CreateUser.Skill", blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "resume"
            self.slug = f"{base}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.candidate.user.email}"