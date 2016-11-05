from django.contrib import admin
from blinky.app.models import System, Worker, HeartBeat


@admin.register(HeartBeat)
class HeartBeatAdmin(admin.ModelAdmin):
    list_filter = ('worker', 'system', 'timestamp')
    list_display = ('hostname', 'pid', 'timestamp',
                    'worker', 'system', 'created_at')


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_filter = ('system',)
    list_display = ('system', 'worker_name', 'created_at')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_filter = ('created_at',)
    list_display = ('system_id', 'created_at')
