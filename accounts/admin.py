from django.contrib import admin
from accounts.models import User, StudentProfile, EmailOTP, Achievement
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "role", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile", "qualification", "college_name", "passing_year", "is_email_verified", "is_application_submitted")
    list_filter = ("is_email_verified", "is_application_submitted")
    search_fields = ("user__email", "user__full_name", "college_name")
    ordering = ("-created_at",)

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "created_at")
    search_fields = ("user__email",)
    ordering = ("-created_at",)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
  
    search_fields = ('created_at',)