import uuid
from django.core.mail import send_mail
from django.conf import settings
from exams.models import ExamResult

from django.contrib.sites.models import Site
from django.urls import reverse

def generate_application_number():
    return f"IMRD{uuid.uuid4().hex[:8].upper()}"



def generate_result(student_exam):
    # 🔐 Prevent duplicate
    result, created = ExamResult.objects.get_or_create(
        student_exam=student_exam,
        defaults={
            "application_number": generate_application_number(),
            "total_questions": 0,
            "correct_answers": 0,
            "total_marks": 0,
            "obtained_marks": 0,
            "percentage": 0,
            "is_pass": False,
            "is_published": False,
        }
    )

    questions = student_exam.exam.questions.all()
    answers = student_exam.answers.all()

    obtained = 0
    correct = 0

    for q in questions:
        ans = answers.filter(question=q).first()
        if ans and ans.selected_option == q.correct_option:
            obtained += q.marks
            correct += 1

    total_marks = sum(q.marks for q in questions)
    percentage = (obtained / total_marks) * 100 if total_marks else 0
    is_pass = obtained >= student_exam.exam.passing_marks

    # ✅ UPDATE existing row
    result.total_questions = questions.count()
    result.correct_answers = correct
    result.total_marks = total_marks
    result.obtained_marks = obtained
    result.percentage = percentage
    result.is_pass = is_pass

    result.save()

    return result



def send_result_email(result):
    site = Site.objects.get_current()

    protocol = "https" if settings.USE_HTTPS else "http"
    result_url = f"{protocol}://{site.domain}{reverse('exams:result_check')}"

    send_mail(
        subject="IMRD Examination Result Published",
        message=f"""
Dear {result.student_exam.student.full_name},

Your exam result has been published successfully.

Application Number: {result.application_number}
Percentage: {result.percentage}%
Status: {"PASS" if result.is_pass else "FAIL"}

Check your result here:
{result_url}

Regards,
IMRD Tech Club
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[result.student_exam.student.email],
        fail_silently=False,
    )