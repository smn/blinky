from blinky.core import celery_app as app
from blinky.core.models import WorkerType, HeartBeat
from blinky.core.signals import worker_online, worker_offline


@app.task
def poll_worker_types():
    worker_types = WorkerType.objects.filter(is_active=True)
    for worker_type in worker_types:
        old_status = worker_type.status
        current_status = (WorkerType.STATUS_ONLINE
                          if worker_type.is_online()
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
    WorkerType.garbage_collect()
    HeartBeat.garbage_collect()
