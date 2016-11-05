from django.contrib import admin
from blinky.app.models import System, Worker, HeartBeat


class HeartBeatAdmin(admin.ModelAdmin):
    list_filter = ('worker', 'system', 'timestamp')
    list_display = ('worker', 'timestamp', 'system')


admin.site.register(System)
admin.site.register(Worker)
admin.site.register(HeartBeat, HeartBeatAdmin)
