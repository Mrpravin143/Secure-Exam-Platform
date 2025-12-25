from django.urls import path
from exams.views import admin_dashboard, export_results_csv


urlpatterns = [
    path("", admin_dashboard, name="admin-dashboard"),
    path("export-results/", export_results_csv, name="export-results"),
]
