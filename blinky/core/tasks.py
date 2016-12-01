from blinky.core import celery_app as app
from django.contrib.auth.models import User


@app.task
def health_check():
    return User.objects.all().count()


@app.task
def poll_worker_types():
    from blinky.core.models import WorkerType
    worker_types = WorkerType.objects.filter(
        is_active=True, status=WorkerType.STATUS_ONLINE)

    for worker_type in worker_types:
        if not worker_type.is_online():
            worker_type.status = WorkerType.STATUS_OFFLINE
            worker_type.save()


@app.task
def garbage_collect():
    from blinky.core.models import WorkerType, HeartBeat
    WorkerType.garbage_collect()
    HeartBeat.garbage_collect()
