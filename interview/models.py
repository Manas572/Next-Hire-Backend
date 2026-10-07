from django.db import models

# Create your models here.
class InterviewQue(models.Model):
    topic = models.CharField(max_length=25)
    question = models.TextField()
    difficulty = models.CharField(max_length=10)
    answer = models.TextField()

    def __str__(self):
        return self.question