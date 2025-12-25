# stage 1 
from rest_framework import serializers
from accounts.models import *
import uuid
from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
# stage 1 

class PersonalInfoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    mobile = serializers.CharField()
    dob = serializers.DateField()
    address = serializers.CharField()

    def create(self, validated_data):
        with transaction.atomic():   # 🔒 important
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                role='student'
            )

            StudentProfile.objects.create(
                user=user,
                mobile=validated_data['mobile'],
                dob=validated_data['dob'],
                address=validated_data['address'],
                application_no="APP" + uuid.uuid4().hex[:8]
            )

        return user
# Stage 2
class EducationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['qualification', 'college_name', 'passing_year']


# Stage 3
class UploadSerializer(serializers.ModelSerializer):
    declaration = serializers.BooleanField(write_only=True)

    class Meta:
        model = StudentProfile
        fields = ['profile_image', 'declaration']

    def validate_declaration(self, value):
        if not value:
            raise serializers.ValidationError("Declaration required")
        return value


# OTP serializer

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()



class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
