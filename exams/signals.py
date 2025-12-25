from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from exams.models import ExamResult


@receiver(post_save, sender=ExamResult)
def send_result_email(sender, instance, created, **kwargs):
    # 👉 ONLY when published
    if instance.is_published:
        send_mail(
            subject="IMRD Examination Result Published",
            message=f"""
Dear Student,

Your exam result has been published successfully.

Application Number: {instance.application_number}

You can check your result using the link below:
http://127.0.0.1:8000/exam/result/check/

Regards,
IMRD Tech Club
R.C. Patel Institute of Management Research and Development
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.student_exam.student.email],
            fail_silently=False,   # 👈 IMPORTANT (errors visible)
        )
