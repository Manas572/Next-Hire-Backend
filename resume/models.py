from django.db import models

# Create your models here.
class ResumeDetails(models.Model):
    class Template(models.TextChoices):
        CLASSIC = "classic", "Classic"
        MODERN = "modern", "Modern"
        MINIMAL = "minimal", "Minimal"

    candidate= models.ForeignKey("CreateUser.CandidateProfile", on_delete=models.CASCADE,related_name="resumes")
    title=models.CharField(max_length=20,default="untitled resume")
    public=models.BooleanField(default=False)
    template=models.CharField(max_length=20,choices=Template.choices,default=Template.CLASSIC)
    accent_color=models.CharField(max_length=20,default="#3B82F6")
    professional_summary=models.TextField(default="")
    dsa_summary=models.TextField(default="")
    included_experiences = models.ManyToManyField("CreateUser.Experience", blank=True)
    included_projects = models.ManyToManyField("CreateUser.Project", blank=True)
    included_educations = models.ManyToManyField("CreateUser.Education", blank=True)
    included_skills = models.ManyToManyField("CreateUser.Skill", blank=True)

    def __str__(self):
        return f"{self.title} - {self.candidate.user.email}"

    
    