from django.contrib import admin
from blinky.core.models import WorkerType
from .models import JunebugInstance


def update_label(modeladmin, request, queryset):
    from .tasks import update_workers_junebug_info
    for junebug in queryset.all():
        for worker in WorkerType.objects.all():
            update_workers_junebug_info.delay(workertype_pk=worker.pk)
update_label.short_description = "Sync WorkerType names"


@admin.register(JunebugInstance)
class JunebugInstanceAdmin(admin.ModelAdmin):
    actions = [update_label]
