from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.utils import timezone
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blinky.settings')

app = Celery('blinky')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0, poll_worker_types.s(),
        name='poll worker types for being offline')
    sender.add_periodic_task(
        60.0, garbage_collect.s(),
        name='garbage collect tasks')


@app.task
def poll_worker_types():
    from blinky.core.models import WorkerType
    from blinky.core.signals import worker_online, worker_offline
    worker_types = WorkerType.objects.filter(is_active=True)
    for worker_type in worker_types:
        old_status = worker_type.status
        # Allow some time for current heartbeats to be processed
        now = timezone.now() - timedelta(
            seconds=worker_type.heartbeat_interval)
        current_status = (WorkerType.STATUS_ONLINE
                          if worker_type.is_online(timestamp=now)
                          else WorkerType.STATUS_OFFLINE)

        if old_status != current_status:
            worker_type.status = current_status
            worker_type.save()
            if current_status == WorkerType.STATUS_ONLINE:
                worker_online.send(sender=WorkerType,
                                   worker_type=worker_type)
            else:
                worker_offline.send(sender=WorkerType,
                                    worker_type=worker_type)


@app.task
def garbage_collect():
    from blinky.core.models import WorkerType, HeartBeat
    WorkerType.garbage_collect()
    HeartBeat.garbage_collect()
