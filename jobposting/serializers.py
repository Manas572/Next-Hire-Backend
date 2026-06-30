from rest_framework import serializers
from .models import Job,Application


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["title", "description", "location", "salary"]

    def validate(self, attrs):
        salary = attrs.get("salary")
        recruiter=self.context["request"].user.recruiter_profile
        title=attrs.get("title")
        if salary is not None and salary <= 0:
            raise serializers.ValidationError({"error": "Salary cannot be less than or equal to 0"})
        
        if Job.objects.filter(recruiter=recruiter,title__iexact=title,is_active=True).exists():
            raise serializers.ValidationError({"error":"Job with Same recruiter already exist with Active Status"})
        
        return attrs
    
class JobApplySerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=["resume_link","portfolio_url","linkedin_url","codolio_url","github_url"]

    def validate(self,attrs):
        candidate=self.context["request"].user.candidate_profile
        job = self.context["job"]
        resume_link=attrs.get("resume_link")
        
        if job.is_active==False :
            raise serializers.ValidationError({"error":"This job is not active"})
        
        if Application.objects.filter(candidate=candidate,job=job).exists():
            raise serializers.ValidationError({"error":"You have applied already"})
        
        return attrs
    
class Listing(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="recruiter.company_name",
        read_only=True
    )
    company_website = serializers.URLField(
        source="recruiter.company_website",
        read_only=True
    )

    class Meta:
        model = Job
        fields = ["id","title","location","salary","description","created_at","company_name","company_website",]
        


