from django.contrib import admin
from blinky.core.models import System, WorkerType, WorkerInstance, HeartBeat


@admin.register(HeartBeat)
class HeartBeatAdmin(admin.ModelAdmin):
    list_filter = ('worker_instance', 'system', 'timestamp')
    list_display = ('worker_instance', 'timestamp', 'created_at')


@admin.register(WorkerType)
class WorkerAdmin(admin.ModelAdmin):
    list_filter = ('system',)
    list_display = (
        'system', 'worker_name', 'worker_friendly_name', 'created_at',
        'online', 'capacity', 'last_seen_at')

    def last_seen_at(self, worker_type):
        last_instance = worker_type.last_seen_instance
        if last_instance:
            return last_instance.last_seen_at


@admin.register(WorkerInstance)
class WorkerInstanceAdmin(admin.ModelAdmin):
    list_filter = ('worker_type',)
    list_display = ('hostname', 'pid', 'worker_type', 'online', 'last_seen_at')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    list_display = ('system_id', 'created_at', 'online')
