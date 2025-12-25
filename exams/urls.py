from django.urls import path
from exams.views import *

app_name = 'exams'

urlpatterns = [
    path('', ExamListView.as_view(), name='exam-list'),
    path('<int:exam_id>/confirm/', ExamConfirmView.as_view(), name='exam-confirm'),
    path('<int:exam_id>/start/', StartExamView.as_view(), name='exam-start'),

    path('<int:student_exam_id>/', ExamScreenView.as_view(), name='exam-screen'),
    path('<int:student_exam_id>/answer/<int:question_id>/', SaveAnswerView.as_view(), name='save-answer'),
    path('<int:student_exam_id>/result/', ExamResultView.as_view(), name='exam-result'),

    path('<int:student_exam_id>/snapshot/',SaveSnapshotView.as_view(),
    name='save-snapshot'),

    path('<int:student_exam_id>/warning/',AddWarningView.as_view(),
    name='add-warning'),

    # resut url's
    path("submit/<int:student_exam_id>/", submit_exam, name="submit-exam"),  # use dash
    path("complete/", exam_complete, name="exam_complete"),

    path("result/check/", result_check, name="result_check"),
    path("result/<int:result_id>/", result_detail, name="result_detail"),
    path("result/<int:result_id>/pdf/", download_result_pdf, name="download_result_pdf"),

    path("result/<int:result_id>/publish/", publish_result, name="publish_result"),

]
