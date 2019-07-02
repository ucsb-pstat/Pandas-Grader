from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/ok/v3/grade/batch", views.grade_batch),
    path("results", views.check_result),
    path("api/ag/v1/fetch_job", views.fetch_job),
    path("api/ag/v1/skeleton/<uuid:assignment_id>", views.get_file),
]
