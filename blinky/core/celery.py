from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

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
    from .tasks import poll_worker_types, garbage_collect
    sender.add_periodic_task(
        60.0, poll_worker_types.s(),
        name='poll worker types for being offline')
    sender.add_periodic_task(
        60.0, garbage_collect.s(),
        name='garbage collect tasks')
