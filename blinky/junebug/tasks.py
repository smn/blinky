from blinky.core import celery_app as app
from blinky.core.models import WorkerType
from blinky.junebug.models import JunebugInstance


@app.task
def update_workers_junebug_info(workertype_pk):
    worker = WorkerType.objects.get(pk=workertype_pk)
    for junebug in JunebugInstance.objects.filter(is_active=True):
        for channel in junebug.get_channels():
            if channel['id'] == worker.worker_name:
                worker.worker_friendly_name = junebug.format_channel_name(
                    channel)
                worker.save()
