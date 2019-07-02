from django.contrib import admin

from . import models


@admin.register(models.Assignment)
class AssignmentInline(admin.ModelAdmin):
    model = models.Assignment
    readonly_fields = ("assignment_id",)


# Register your models here.
# admin.site.register(
#     models.Assignment, AssignmentInline
# )
admin.site.register(models.GradingJob)
