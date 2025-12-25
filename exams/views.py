from django.shortcuts import render, redirect

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from exams.models import *
from exams.serializers import (
    ExamSerializer,
    StartExamSerializer,
    StudentExamStatusSerializer
)
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from exams.utils import generate_result
from django.core.mail import send_mail

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

from django.utils import timezone
from exams.utils import generate_result, send_result_email
from django.contrib.admin.views.decorators import staff_member_required

from accounts.models import StudentProfile, User
import csv
import os
from django.conf import settings




class ExamListView(LoginRequiredMixin,View):
    login_url = 'login'
    def get(self, request):
        exams = Exam.objects.filter(is_active=True)

        return render(request, 'exams/exam_list.html', {
            'exams': exams
        })


class ExamConfirmView(LoginRequiredMixin,View):
    login_url ='login'
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        return render(request, 'exams/exam_confirm.html', {
            'exam': exam
        })


class StartExamView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, exam_id):

        exam = get_object_or_404(Exam, id=exam_id)

        student_exam, created = StudentExam.objects.get_or_create(
            student=request.user,
            exam=exam,
        )

        if not student_exam.start_time:
            student_exam.start_time = timezone.now()
            student_exam.save()

        print("START USER:", request.user, request.user.is_authenticated)


        return redirect('exams:exam-screen', student_exam.id)


class ExamScreenView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, student_exam_id):
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)

        student_exam = get_object_or_404(
            StudentExam,
            id=student_exam_id,
            student=request.user
        )

        if student_exam.is_submitted:
            return redirect('exams:exam_complete')

        if not student_exam.start_time:
            return redirect('exams:exam-list')

        exam = student_exam.exam
        questions = exam.questions.all()

        elapsed = (timezone.now() - student_exam.start_time).total_seconds()
        remaining = max(0, exam.duration_minutes * 60 - int(elapsed))

        if remaining == 0:
            return redirect('exams:submit-exam', student_exam.id)

        answers = {
            a.question_id: a.selected_option
            for a in student_exam.answers.all()
        }

        return render(request, 'exams/exam_screen.html', {
            'student_exam': student_exam,
            'questions': questions,
            'answers': answers,
            'remaining_seconds': remaining
        })



class SaveAnswerView(LoginRequiredMixin,View):
    login_url ='login'
    def post(self, request, student_exam_id, question_id):
        student_exam = get_object_or_404(
            StudentExam,
            id=student_exam_id,
            student=request.user
        )

        selected = request.POST.get('option')

        Answer.objects.update_or_create(
            student_exam=student_exam,
            question_id=question_id,
            defaults={'selected_option': selected}
        )

        return redirect('exams:exam-screen', student_exam.id)





class ExamResultView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, student_exam_id):
        student_exam = get_object_or_404(
            StudentExam,
            id=student_exam_id,
            student=request.user
        )

        total = 0
        obtained = 0

        for ans in student_exam.answers.select_related('question'):
            total += ans.question.marks
            if ans.selected_option == ans.question.correct_option:
                obtained += ans.question.marks

        passing_marks = student_exam.exam.passing_marks
        result_status = "PASS" if obtained >= passing_marks else "FAIL"

        return render(request, 'exams/result.html', {
            'exam': student_exam.exam,
            'total_marks': total,
            'obtained_marks': obtained,
            'passing_marks': passing_marks,
            'result_status': result_status
        })


import base64
from django.core.files.base import ContentFile

class SaveSnapshotView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, student_exam_id):
        student_exam = get_object_or_404(
            StudentExam,
            id=student_exam_id,
            student=request.user
        )

        img_data = request.POST.get('image')
        if not img_data:
            return JsonResponse({'error': 'No image'}, status=400)

        format, imgstr = img_data.split(';base64,')
        ext = format.split('/')[-1]

        image = ContentFile(
            base64.b64decode(imgstr),
            name=f'snapshot_{timezone.now().timestamp()}.{ext}'
        )

        ExamSnapshot.objects.create(
            student_exam=student_exam,
            image=image
        )

        return JsonResponse({'status': 'ok'})



class AddWarningView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, student_exam_id):
        student_exam = get_object_or_404(
            StudentExam,
            id=student_exam_id,
            student=request.user
        )

        # 🔒 HARD LIMIT
        if student_exam.warnings >= 3:
            return JsonResponse({"warnings": 3})

        student_exam.warnings += 1
        student_exam.save()

        if student_exam.warnings >= 3:
            student_exam.is_submitted = True
            student_exam.end_time = timezone.now()
            student_exam.save()

        return JsonResponse({"warnings": student_exam.warnings})

def exam_complete(request):
    return render(request, "exams/exam_complete.html")



def submit_exam(request, student_exam_id):
    student_exam = get_object_or_404(StudentExam, id=student_exam_id)

    if student_exam.is_submitted:
        return redirect("exams:exam_complete")

    student_exam.is_submitted = True
    student_exam.end_time = timezone.now()
    student_exam.save()

    result = generate_result(student_exam)
    print("RESULT SAVED ✅:", result.id)  # 👈 TEMP DEBUG

    return redirect("exams:exam_complete")


# published result only access करु शकतील
def publish_result(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id)

    if not result.is_published:
        result.is_published = True
        result.save()

        send_result_email(result)   # 📧 EMAIL HERE

    return redirect("admin:exams_examresult_changelist")




def result_check(request):
    if request.method == "POST":
        app_no = request.POST.get("application_number")
        email = request.POST.get("email")

        result = ExamResult.objects.filter(
            application_number=app_no,
            student_exam__student__email=email,
            is_published=True
        ).first()

        if result:
            return redirect("exams:result_detail", result.id)

        return render(request, "exams/result_check.html", {
            "error": "Result not published yet"
        })

    return render(request, "exams/result_check.html")



def result_detail(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id)

    if not result.is_published:
        return render(request, "exams/result_not_published.html")

    questions = result.student_exam.exam.questions.all()
    answers = result.student_exam.answers.all()

    data = []
    for i, q in enumerate(questions, start=1):
        ans = answers.filter(question=q).first()
        status = "Right" if ans and ans.selected_option == q.correct_option else "Wrong"
        marks = q.marks if status == "Right" else 0

        data.append({
            "no": i,
            "question": q.question_text,
            "status": status,
            "marks": marks
        })

    return render(request, "exams/result_detail.html", {
        "result": result,
        "data": data
    })



def download_result_pdf(request, result_id):
    result = get_object_or_404(ExamResult, id=result_id)

    if not result.is_published:
        return HttpResponse("Result not published")

    # Question-wise data
    questions = result.student_exam.exam.questions.all()
    answers = result.student_exam.answers.all()
    data = []
    for i, q in enumerate(questions, start=1):
        ans = answers.filter(question=q).first()
        status = "Right" if ans and ans.selected_option == q.correct_option else "Wrong"
        marks = q.marks if status == "Right" else 0
        data.append({
            "no": i,
            "question": q.question_text,
            "status": status,
            "marks": marks
        })

    # Absolute paths for images
    static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
    college_logo = os.path.join(static_dir, "images/RCP.png")
    techclub_logo = os.path.join(static_dir, "images/TechClub.png")
    default_profile = os.path.join(static_dir, "images/default_profile.png")

    context = {
        "result": result,
        "data": data,
        "college_logo": college_logo,
        "techclub_logo": techclub_logo,
        "default_profile": default_profile
    }

    # Use relative template path
    template = get_template("exams/result_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="IMRD_Result.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response



# admin dashboard view

@staff_member_required
def admin_dashboard(request):

    results = ExamResult.objects.select_related(
        "student_exam__student"
    ).filter(is_published=True)

    context = {
        # COUNTS
        "total_students": User.objects.filter(role="student").count(),
        "total_exams": Exam.objects.count(),
        "active_exams": Exam.objects.filter(is_active=True).count(),
        "submitted_exams": StudentExam.objects.filter(is_submitted=True).count(),

        # PASS / FAIL
        "pass_count": ExamResult.objects.filter(is_pass=True).count(),
        "fail_count": ExamResult.objects.filter(is_pass=False).count(),

        # TABLE DATA
        "results": results,
    }

    return render(request, "admin/custom_dashboard.html", context)

@staff_member_required
def export_results_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="exam_results.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Student Name",
        "Mobile Number",
        "Percentage",
        "Status"
    ])

    results = ExamResult.objects.select_related(
        "student_exam__student"
    )

    for result in results:
        student = result.student_exam.student
        profile = StudentProfile.objects.filter(user=student).first()

        writer.writerow([
            student.full_name,
            profile.mobile if profile else "",
            result.percentage,
            "PASS" if result.is_pass else "FAIL"
        ])

    return response