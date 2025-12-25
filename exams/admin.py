from django.contrib import admin
from exams.models import Exam, Question, StudentExam, Answer, ExamSnapshot, ExamResult

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_minutes", "total_marks", "passing_marks", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("-id",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question_text", "correct_option", "marks")
    list_filter = ("exam",)
    search_fields = ("question_text",)
    ordering = ("-id",)

@admin.register(StudentExam)
class StudentExamAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "start_time", "end_time", "warnings", "is_submitted")
    list_filter = ("is_submitted", "exam")
    search_fields = ("student__email", "exam__title")
    ordering = ("-start_time",)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "question", "selected_option")
    search_fields = ("student_exam__student__email", "question__question_text")
    ordering = ("-id",)

@admin.register(ExamSnapshot)
class ExamSnapshotAdmin(admin.ModelAdmin):
    list_display = ("student_exam", "image", "created_at")
    search_fields = ("student_exam__student__email",)
    ordering = ("-created_at",)

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("application_number", "student_exam", "total_marks", "obtained_marks", "percentage", "is_pass", "is_published", "generated_at")
    list_filter = ("is_pass", "is_published")
    search_fields = ("application_number", "student_exam__student__email", "student_exam__exam__title")
    ordering = ("-generated_at",)
