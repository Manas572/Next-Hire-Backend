from django.contrib import admin
from django.urls import path
from CreateUser.views import reg_candidate,reg_recruiter,education_register,project_register,experience_register,CandidateProfileView,EducationListView,ExperienceListView,ProjectListView,ProjectUpd,ExperienceUpd,EducationUpd,skilllist
from jobposting.views import CreateJob,ListAlljob,ApplyJob,JobDetail
from resume.views import resume_register
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from ninja import NinjaAPI
from interview.api import interview_router
from interview.views import  get_question
from cf.api import api as cf_api

api = NinjaAPI()
api.add_router("", interview_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path("api/cf/", cf_api.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("createcandiate/",reg_candidate.as_view(),name="Register_Candidate"),
    path("me/",CandidateProfileView.as_view(),name="Candidate_profile"),
    path("edu/",EducationListView.as_view(),name="education_info"),
    path("exp/",ExperienceListView.as_view(),name="experience_info"),
    path("pro/",ProjectListView.as_view(),name="project_info"),
    path("eduupd/<int:pk>/",EducationUpd.as_view(),name="education_update"),
    path("expupd/<int:pk>/",ExperienceUpd.as_view(),name="experience_update"),
    path("proupd/<int:pk>/",ProjectUpd.as_view(),name="project_update"),
    path("createrecruiter/",reg_recruiter.as_view(),name="Register_recruiter"),
    path("education/",education_register.as_view(),name="education_register"),
    path("experience/",experience_register.as_view(),name="experience_register"),
    path("project/",project_register.as_view(),name="project_register"),
    path("createjob/",CreateJob.as_view(),name="Create_job"),
    path("createresume/",resume_register.as_view(),name="Create_resume"),
    path("listjob/",ListAlljob.as_view(),name="List_job"),
    path("listjob/<int:pk>/", JobDetail.as_view(), name="job-detail"),
    path("apply/<int:pk>/", ApplyJob.as_view(), name="apply-detail"),
    path("skills/",skilllist.as_view(),name="skill_set"),
    path("interviewquestion/",get_question,name="interview_question")
]
