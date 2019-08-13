from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from . import models


@admin.register(models.Assignment)
class AssignmentInline(admin.ModelAdmin):
    model = models.Assignment
    readonly_fields = ("assignment_id",)


@admin.register(models.GradingJob)
class GradingJobAdmin(admin.ModelAdmin):
    class Media:
        js = ("js/admin/custom_admin.js",)

    model = models.GradingJob
    list_display = [
        "assignment",
        "backup_id",
        "enqueued_time",
        "finish_time",
        "show_log_url",
    ]
    # ordered by task submission time and finish time, in reverse order
    ordering = ["-enqueued_time", "-finish_time"]
    date_hierarchy = "finish_time"
    list_filter = ["assignment"]
    search_fields = ["backup_id"]

    # TODO: add a link here to view log html
    def show_log_url(self, obj):
        return format_html(
            "<a href='{url}'>View Log</a>",
            url=reverse("get_job_log", kwargs={"job_id": obj.job_id}),
        )

    show_log_url.short_description = "Go to log"
