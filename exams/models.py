from django.db import models
from accounts.models import User
from django.utils import timezone
# Create your models here.


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField(default=25, null=True, blank=True) 

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    CORRECT_CHOICES = (
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    )
    correct_option = models.CharField(max_length=1, choices=CORRECT_CHOICES)

    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text[:50]



class StudentExam(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    warnings = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.email} - {self.exam.title}"

        

class Answer(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)

    class Meta:
        unique_together = ('student_exam', 'question')

    def __str__(self):
        return f"{self.question.id} - {self.selected_option}"


class ExamSnapshot(models.Model):
    student_exam = models.ForeignKey(StudentExam, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="exam_snapshots/")
    created_at = models.DateTimeField(auto_now_add=True)





# Result Model to store exam results
class ExamResult(models.Model):
    student_exam = models.OneToOneField(StudentExam, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=20, unique=True)

    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    total_marks = models.IntegerField()
    obtained_marks = models.IntegerField()
    percentage = models.FloatField()
    is_pass = models.BooleanField()
    is_published = models.BooleanField(default=False)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.application_number
