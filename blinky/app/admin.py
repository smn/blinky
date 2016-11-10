from django.contrib import admin
from blinky.app.models import System, WorkerType, WorkerInstance, HeartBeat


@admin.register(HeartBeat)
class HeartBeatAdmin(admin.ModelAdmin):
    list_filter = ('worker_instance', 'system', 'timestamp')
    list_display = ('worker_instance', 'timestamp', 'created_at')


@admin.register(WorkerType)
class WorkerAdmin(admin.ModelAdmin):
    list_filter = ('system',)
    list_display = ('system', 'worker_name', 'created_at')


@admin.register(WorkerInstance)
class WorkerInstanceAdmin(admin.ModelAdmin):
    list_filter = ('worker_type',)
    list_display = ('hostname', 'pid', 'worker_type')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    list_display = ('system_id', 'created_at')
