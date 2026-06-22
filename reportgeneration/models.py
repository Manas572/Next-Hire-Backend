from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class AnalysisReport(models.Model):
    candidate = models.ForeignKey(
        "CreateUser.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="reports"
    )
    job=models.ForeignKey(
        "jobposting.Job",
        on_delete=models.CASCADE,
        related_name="reports"
    )
    resume_text = models.TextField()
    match_score = models.PositiveSmallIntegerField(validators=[ MinValueValidator(0),MaxValueValidator(100)])
    technical_questions = models.JSONField(default=list)
    behavioral_questions = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    preparation_plan = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
