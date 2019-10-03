from django.db import models
import uuid
import enum
from django.utils import timezone
import time


def get_file_path(instance, filename: str):
    return f"uploads/{instance.name}/{instance.assignment_id}/{time.time()}-{filename}"


# Create your models here.
class Assignment(models.Model):
    assignment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Use thie field as okpy's autograder_key",
    )

    name = models.CharField(max_length=20)
    last_updated = models.DateTimeField(default=timezone.now)
    file = models.FileField(
        upload_to=get_file_path, help_text="Please upload a zip file!"
    )

    def __str__(self):
        return f"{self.name}/{self.assignment_id}"


class JobStatusEnum(enum.Enum):
    QUEUED = "QUEUED"
    DONE = "DONE"
    RUNNING = "RUNNING"

    # deprecated
    FINISHED = "FINISHED"


def translate_okpy_status(status):
    return {
        "JobStatusEnum.QUEUED": "queued",
        "JobStatusEnum.DONE": "finished",
        "JobStatusEnum.RUNNING": "running",
    }[status]


class GradingJob(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # constructor fields
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)
    backup_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=50)

    # automatic metadata
    status = models.CharField(
        max_length=255,
        choices=[(tag, tag.value) for tag in JobStatusEnum],
        default=JobStatusEnum.QUEUED,
    )
    enqueued_time = models.DateTimeField(default=timezone.now)
    dequeue_time = models.DateTimeField(null=True)
    finish_time = models.DateTimeField(null=True)

    # post hoc data
    log_html = models.TextField(null=True)

    def __str__(self):
        return f"{self.assignment.name}-{self.backup_id}"

    def dequeue(self):
        self.dequeue_time = timezone.now()
        self.status = JobStatusEnum.RUNNING

    def requeue(self):
        self.dequeue_time = models.DateTimeField(null=True)
        self.status = JobStatusEnum.QUEUED

    def done(self):
        self.finish_time = timezone.now()
        self.status = JobStatusEnum.DONE
