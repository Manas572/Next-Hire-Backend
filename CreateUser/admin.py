from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CandidateProfile, RecruiterProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('email', 'role')
    ordering = ('-created_at',)

    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('User Type', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'role', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')



class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'interview_practice_score', 'created_at')
    search_fields = ('user__email',)

class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('company_name', 'user__email')

admin.site.register(CandidateProfile, CandidateProfileAdmin)
admin.site.register(RecruiterProfile, RecruiterProfileAdmin)