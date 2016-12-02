from blinky.core import celery_app as app
from django.contrib.auth.models import User


@app.task
def health_check():
    return User.objects.all().count()


@app.task
def poll_worker_types():
    from blinky.core.models import WorkerType
    from blinky.core.signals import worker_online, worker_offline

    worker_types = WorkerType.objects.filter(is_active=True)

    for worker_type in worker_types:
        if ((worker_type.status == WorkerType.STATUS_ONLINE or
             worker_type.status == WorkerType.STATUS_UNKNOWN) and
                not worker_type.is_alive()):
            worker_type.status = WorkerType.STATUS_OFFLINE
            worker_type.save()
            worker_offline.send(sender=WorkerType, worker_type=worker_type)
            # If this happens don't try and check if it's online again
            # this run
            continue

        if ((worker_type.status == WorkerType.STATUS_OFFLINE or
             worker_type.status == WorkerType.STATUS_UNKNOWN) and
                worker_type.is_alive()):
            worker_type.status = WorkerType.STATUS_ONLINE
            worker_type.save()
            worker_online.send(sender=WorkerType, worker_type=worker_type)
            continue


@app.task
def garbage_collect():
    from blinky.core.models import HeartBeat
    HeartBeat.garbage_collect()
