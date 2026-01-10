from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


from django.utils import timezone
from datetime import timedelta

from accounts.managers import UserManager



class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return self.email



class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Stage 1 – Personal Info
    mobile = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField()

    # Stage 2 – Educational Info
    qualification = models.CharField(max_length=100, null=True, blank=True)
    college_name = models.CharField(max_length=150, null=True, blank=True)
    passing_year = models.IntegerField(null=True, blank=True)

    # Stage 3 – Uploads
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Workflow flags
    application_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False, null=True, blank=True)
    is_application_submitted = models.BooleanField(default=False, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)




class EmailOTP(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE,  null=True, blank=True)
    otp = models.CharField(max_length=6,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)

    def is_valid(self):
        """Check OTP expiry (5 mins)"""
        return timezone.now() <= self.created_at + timedelta(minutes=5)


# Achivements
class Achievement(models.Model):
  
    image = models.ImageField(upload_to='achievements/')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
