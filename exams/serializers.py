from rest_framework import serializers
from exams.models import *
from django.utils import timezone


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'duration_minutes', 'total_marks']



class StartExamSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()

    def validate_exam_id(self, value):
        if not Exam.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Exam not available")
        return value

    def create(self, validated_data):
        request = self.context['request']
        student = request.user
        exam = Exam.objects.get(id=validated_data['exam_id'])

        student_exam, created = StudentExam.objects.get_or_create(
            student=student,
            exam=exam
        )

        if student_exam.start_time:
            raise serializers.ValidationError("Exam already started")

        student_exam.start_time = timezone.now()
        student_exam.save()

        return student_exam


class StudentExamStatusSerializer(serializers.ModelSerializer):
    remaining_time_seconds = serializers.SerializerMethodField()

    class Meta:
        model = StudentExam
        fields = [
            'id',
            'start_time',
            'end_time',
            'warnings',
            'is_submitted',
            'remaining_time_seconds'
        ]

    def get_remaining_time_seconds(self, obj):
        if not obj.start_time or obj.is_submitted:
            return 0

        now = timezone.now()
        duration = obj.exam.duration_minutes * 60
        elapsed = (now - obj.start_time).total_seconds()
        remaining = max(0, duration - elapsed)

        return int(remaining)




