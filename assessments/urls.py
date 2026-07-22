from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("assessments/new/", views.assessment_create, name="assessment-create"),
    path("assessments/<int:pk>/", views.assessment_detail, name="assessment-detail"),
    path("assessments/<int:assessment_pk>/questions/<int:question_pk>/", views.response_edit, name="response-edit"),
    path("assessments/<int:pk>/transition/", views.assessment_transition, name="assessment-transition"),
    path("assessments/<int:pk>/report.json", views.assessment_report, name="assessment-report"),
]
