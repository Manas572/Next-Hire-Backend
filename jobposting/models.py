from django.db import models
from django.db.models import Q, UniqueConstraint
# Create your models here.
class Job(models.Model):
    recruiter = models.ForeignKey(
        "CreateUser.RecruiterProfile",
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=255, db_index=True)
    salary = models.DecimalField(max_digits=12,decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
        UniqueConstraint(
            fields=["recruiter", "title"],
            condition=Q(is_active=True),
            name="unique_job"
        )
    ]


class Application(models.Model):
    candidate=models.ForeignKey(
        "CreateUser.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="applications"
    )
    job=models.ForeignKey(
        "Job",
        on_delete=models.CASCADE,
        related_name="applications"
    )
    class Status(models.TextChoices):
        PENDING="PENDING","Pending"
        ACCEPTED="ACCEPTED","Accepted"
        REJECTED="REJECTED","Rejected"

    resume_link=models.URLField(max_length=200);
    portfolio_url=models.URLField(max_length=150,blank=True)
    linkedin_url=models.URLField(max_length=150,blank=True)
    github_url=models.URLField(max_length=150,blank=True)
    codolio_url=models.URLField(max_length=150,blank=True)

    statustype=models.CharField(max_length=10,choices=Status.choices,default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["candidate","job"],
                name="unique_job_and_candidate"
            )
        ]
    

