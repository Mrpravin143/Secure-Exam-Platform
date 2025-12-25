from django.shortcuts import render, redirect
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import *
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import get_user_model


from rest_framework.permissions import IsAuthenticated

import random
from django.core.mail import send_mail
from accounts.models import *

from django.views import View
from django.conf import settings
from reportlab.lib.colors import black, red, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas





class PersonalInfoView(View):

    def get(self, request):
        return render(request, 'registration/personal_info.html')

    def post(self, request):
        serializer = PersonalInfoSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            # 🔥 Save user id in session for next stage
            request.session['reg_user_id'] = user.id
            return redirect('education-info')

        return render(request, 'registration/personal_info.html', {
            'errors': serializer.errors
        })


class EducationInfoView(View):

    def get(self, request):
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        if not hasattr(user, 'studentprofile'):
            return redirect('personal-info')

        return render(request, 'registration/education_info.html')

    def post(self, request):
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        profile = user.studentprofile

        serializer = EducationInfoSerializer(profile, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('upload-info')  # 🔥 Proper next stage

        return render(request, 'registration/education_info.html', {
            'errors': serializer.errors
        })



class UploadInfoView(APIView):
    def get(self, request):
        # Optional: check session
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        if not hasattr(user, 'studentprofile'):
            return redirect('personal-info')

        return render(request, 'registration/upload_declaration.html')

    def post(self, request):
        user_id = request.session.get('reg_user_id')
        user = User.objects.get(id=user_id)
        profile = user.studentprofile

        serializer = UploadSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save(is_application_submitted=True)
            return redirect('send-otp')

        return render(request, 'registration/upload_declaration.html', {
            'errors': serializer.errors
        })



# -----------------------------
# Send OTP View
# -----------------------------
class SendOTPView(View):
    def get(self, request):
        """Page open for OTP"""
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')
        return render(request, 'registration/send_otp.html')

    def post(self, request):
        """Generate OTP, save, and send email"""
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP in DB (update if exists)
        EmailOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        # Send email
        send_mail(
            subject='IMRD Tech Club - Email Verification OTP',
            message=f'Your OTP is {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False   # True असेल तर error कळणार नाही
        )


        # Redirect to verify OTP page
        return redirect('verify-otp')


# -----------------------------
# Verify OTP View
# -----------------------------
class VerifyOTPView(View):
    def get(self, request):
        """Render OTP input page"""
        return render(request, 'registration/otp_verify.html')

    def post(self, request):
        """Check entered OTP"""
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        otp_entered = request.POST.get('otp')

        # Get OTP object
        otp_obj = EmailOTP.objects.filter(user=user).first()
        if not otp_obj:
            return render(request, 'registration/otp_verify.html', {
                'error': 'OTP not found'
            })

        # Validate OTP
        if otp_obj.otp == otp_entered and otp_obj.is_valid():
            # Mark student profile verified
            profile = user.studentprofile
            profile.is_email_verified = True
            profile.save()

            # Delete OTP after use
            otp_obj.delete()

            # Redirect to application view
            return redirect('view-application')

        # Invalid OTP
        return render(request, 'registration/otp_verify.html', {
            'error': 'Invalid or Expired OTP'
        })




class ApplicationView(View):
    def get(self, request):
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        profile = user.studentprofile
        return render(request, 'application/application_form.html', {
            'profile': profile
        })

import os



class DownloadApplicationView(View):

    def get(self, request):
        user_id = request.session.get('reg_user_id')
        if not user_id:
            return redirect('personal-info')

        user = User.objects.get(id=user_id)
        profile = user.studentprofile

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="IMRD_Application_Form.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        # ================= HEADER =================
        p.setFont("Helvetica-Bold", 22)
        p.setFillColor(HexColor("#003366"))  # Dark Blue
        p.drawCentredString(width / 2, height - 50, "IMRD Tech Club")

        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(black)
        p.drawCentredString(width / 2, height - 85, "Application Form")

        # ================= PROFILE IMAGE =================
        if profile.profile_image:
            img_path = os.path.join(settings.MEDIA_ROOT, profile.profile_image.name)
            if os.path.exists(img_path):
                p.drawImage(img_path, width - 150, height - 190, 100, 120, mask='auto')

        # ================= BASIC DETAILS =================
        p.setFont("Helvetica-Bold", 13)
        p.drawString(40, height - 140, "Personal Details")

        p.setFont("Helvetica", 11)
        y = height - 165
        gap = 18

        personal_details = [
            ("Full Name", user.full_name),
            ("Email", user.email),
            ("Mobile", profile.mobile),
            ("Date of Birth", str(profile.dob)),
            ("Application No", profile.application_no),
        ]

        for label, value in personal_details:
            p.drawString(50, y, f"{label} : {value}")
            y -= gap

        # ================= EDUCATION DETAILS =================
        y -= 10
        p.setFont("Helvetica-Bold", 13)
        p.drawString(40, y, "Educational Details")
        y -= 20

        p.setFont("Helvetica", 11)
        education_details = [
            ("Qualification", profile.qualification),
            ("College / Institute", profile.college_name),
            ("Passing Year", profile.passing_year),
        ]

        for label, value in education_details:
            p.drawString(50, y, f"{label} : {value}")
            y -= gap

        # ================= GUIDELINES =================
        y -= 15
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(red)
        p.drawString(40, y, "Important Guidelines:")
        y -= 18

        p.setFont("Helvetica", 11)
        guidelines = [
            "1. Ensure all information provided is accurate.",
            "2. Application once submitted cannot be modified.",
            "3. Keep a copy of this application for future reference.",
            "4. Any false information may lead to disqualification.",
        ]

        for line in guidelines:
            p.drawString(50, y, line)
            y -= gap

        # ================= FOOTER DECLARATION =================
        y -= 20
        p.setFillColor(black)
        p.setFont("Helvetica", 10)
        p.drawString(
            40, y,
            "I hereby declare that the information provided above is true and correct to the best of my knowledge."
        )

        p.showPage()
        p.save()

        return response



User = get_user_model()

class LoginView(View):

    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        serializer = LoginSerializer(data=request.POST)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # 🔐 IMPORTANT: Session login
            django_login(request, user)

            # (Optional) JWT tokens if needed for APIs
            request.session['access_token'] = serializer.validated_data['access']
            request.session['refresh_token'] = serializer.validated_data['refresh']

            
            print("LOGIN SUCCESS:", user.email)
            print("AUTH:", user.is_authenticated)

            return redirect('exams:exam-list')

        return render(request, 'auth/login.html', {
            'error': 'Invalid credentials'
        })


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')


