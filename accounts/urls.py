from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/personal/', PersonalInfoView.as_view(), name='personal-info'),
    path('register/education/', EducationInfoView.as_view(), name='education-info'),
    path('register/upload/', UploadInfoView.as_view(), name='upload-info'),
    path('register/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('register/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('application/view/', ApplicationView.as_view(), name='view-application'),
    path('application/download/', DownloadApplicationView.as_view(), name='download-application'),
    path('login/', LoginView.as_view(), name='login'),
    # urls.py
    path('logout/', logout_view, name='logout'),

]


