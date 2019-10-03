from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse
from django.views.decorators.http import require_POST
import json
from constance import config
from .models import Assignment, GradingJob, JobStatusEnum, translate_okpy_status
from django.db import transaction
from .k8s import add_k_workers

# Help with debugging
from ipware import get_client_ip


def index(request: HttpRequest):
    return redirect("admin:index")


def _get_assignment(file_id):
    query = Assignment.objects.filter(assignment_id=file_id)
    result = get_object_or_404(query)
    return result


@require_POST
@transaction.atomic
def grade_batch(request: HttpRequest):
    """
    Pretty sure okpy hits this up when I submit an autograder job. 
    I think what happens here is that I allocate an equal number of workers 
    as the number of jobs (backupids). I believe only one backupd is submitted 
    each time.  
    """
    print("==============================")
    print('GRADE BATCH START')

    # The okpy server should be sending us the access token and backup id, which will 
    # let us download assignments. Based on the assignment key, we also know which of the 
    # uploaded assignments to use.
    req_data = json.loads(request.body)
    access_token = req_data["access_token"]
    backup_ids = req_data["subm_ids"]
    print(backup_ids)

    assignment_key = req_data["assignment"]
    assignment = _get_assignment(assignment_key)

    print("Request data")
    print(req_data)
    
    # Here we allocate kubernetes workers. 
    print("Allocate workers")
    add_k_workers(len(backup_ids))
    
    # I think the saving job stuff is just for the UI. 
    # TODO(simon):
    # Address the issue of queue backpresssure:
    # specifically, okpy has a short retry period.
    # we need to check if the backup_id is already in queue
    # to avoid creating another task
    job_ids = []
    for backup_id in backup_ids:
        print("Lenths:")
        print(len(backup_id), backup_id)
        job = GradingJob(
            assignment=assignment, backup_id=backup_id, access_token=access_token
        )
        job.save()

        job_ids.append(job.job_id)
    
    print(job_ids) 
    print("GRADE BATCH END")
    print("==============================")
    return JsonResponse({"jobs": job_ids})


@require_POST
def check_result(request):
    jobs_ids = json.loads(request.body)
    status = {}
    for job_id in jobs_ids:
        job = GradingJob.objects.get(job_id=job_id)
        # str.split is used to normalized enum name
        status[job_id] = {"status": translate_okpy_status(job.status)}
    return JsonResponse(status)


def fetch_job(request):
    queued_jobs = GradingJob.objects.filter(status=JobStatusEnum.QUEUED).order_by(
        "enqueued_time"
    )
    if len(queued_jobs) == 0:
        print("empty queue")
        return JsonResponse({"queue_empty": True})
    else:
        next_job = queued_jobs[0]
        next_job.dequeue()
        next_job.save()
        print("FETCH HAS JOB")
        print(next_job)
        j = {
                "queue_empty": False,
                "skeleton": next_job.assignment.assignment_id,
                "backup_id": next_job.backup_id,
                "access_token": next_job.access_token,
                "job_id": next_job.job_id,
            }
        print(j)
        print("fetch done")

        return JsonResponse(
            {
                "queue_empty": False,
                "skeleton": next_job.assignment.assignment_id,
                "backup_id": next_job.backup_id,
                "access_token": next_job.access_token,
                "job_id": next_job.job_id,
            }
        )


def get_file(request: HttpRequest, assignment_id):
    file = _get_assignment(assignment_id).file
    return FileResponse(file)

def add_kube_workers(request: HttpRequest, num_workers):
    # Hacky solution to spin up more workers to pick up orphaned task
    add_k_workers(int(num_workers))
    return HttpResponse("Workers added you hack")

def requeue_jobs(request, access_token):
    # Hacky solution to reque running jobs 
    query = GradingJob.objects.filter(status=JobStatusEnum.RUNNING, access_token=access_token)
    for q in query:
        q.requeue()
        q.save()
    return HttpResponse("Running jobs requeued")


@require_POST
def report_done(request: HttpRequest, job_id):
    query = GradingJob.objects.filter(job_id=job_id)
    result = get_object_or_404(query)

    result.done()
    result.log_html = request.body.decode()

    result.save()
    print("Report done")
    print(request.body.decode())
    return HttpResponse(status=200)


def get_job_log(request: HttpRequest, job_id):
    query = GradingJob.objects.filter(job_id=job_id)
    result = get_object_or_404(query)
    return HttpResponse(result.log_html)
