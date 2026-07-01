from django.contrib import admin
from django.urls import path
from CreateUser.views import reg_candidate,reg_recruiter,education_register,project_register,experience_register,CandidateProfileView
from jobposting.views import CreateJob,ListAlljob,ApplyJob,JobDetail
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("createcandiate/",reg_candidate.as_view(),name="Register_Candidate"),
    path("me/",CandidateProfileView.as_view(),name="Candidate_profile"),
    path("createrecruiter/",reg_recruiter.as_view(),name="Register_recruiter"),
    path("education/",education_register.as_view(),name="education_recruiter"),
    path("experience/",experience_register.as_view(),name="experience_recruiter"),
    path("project/",project_register.as_view(),name="project_recruiter"),
    path("createjob/",CreateJob.as_view(),name="Create_job"),
    path("listjob/",ListAlljob.as_view(),name="List_job"),
    path("listjob/<int:pk>/", JobDetail.as_view(), name="job-detail"),
    path("apply/<int:pk>/", ApplyJob.as_view(), name="job-detail"),
]
