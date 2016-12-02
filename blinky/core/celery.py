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
app.conf.beat_schedule = {
    'poll worker types for being offline': {
        'task': 'blinky.core.tasks.poll_worker_types',
        'schedule': 60.0,
        'args': (),
    },
    'garbage collect tasks': {
        'task': 'blinky.core.tasks.garbage_collect',
        'schedule': 60.0,
        'args': (),
    }
}
