from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/ok/v3/grade/batch", views.grade_batch),
    path("results", views.check_result),
    path("api/ag/v1/fetch_job", views.fetch_job),
    path("api/ag/v1/skeleton/<uuid:assignment_id>", views.get_file),
    path("api/ag/v1/report_done/<uuid:job_id>", views.report_done),
    path("api/ag/v1/get_job_log/<uuid:job_id>", views.get_job_log, name="get_job_log"),
    path("api/ag/v1/add_kube_workers/<int:num_workers>", views.add_kube_workers),
    path("api/ag/v1/requeue_jobs/<str:access_token>", views.requeue_jobs),
]
