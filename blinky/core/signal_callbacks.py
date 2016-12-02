from .signals import worker_capacity_change
from .models import WorkerType


def post_save_heartbeat(sender, instance, created, **kwargs):
    previous_heartbeat = instance.previous()
    if not previous_heartbeat:
        return

    timestamp = previous_heartbeat.timestamp

    worker_type = instance.worker_type
    worker_type.status = (WorkerType.STATUS_ONLINE
                          if worker_type.is_alive()
                          else WorkerType.STATUS_OFFLINE)
    worker_type.save()

    current_capacity = worker_type.capacity()
    if current_capacity != worker_type.capacity(timestamp):
        worker_capacity_change.send(sender=worker_type.__class__,
                                    worker_type=worker_type,
                                    capacity=current_capacity)


def pre_save_worker_type(sender, instance, raw, **kwargs):
    worker_type = instance
    try:
        db_worker_type = WorkerType.objects.get(pk=worker_type.pk)
    except WorkerType.DoesNotExist:
        return

    from blinky.core.signals import worker_online, worker_offline

    current_status = worker_type.status
    old_status = db_worker_type.status
    if old_status != current_status:
        if current_status == WorkerType.STATUS_ONLINE:
            worker_online.send(sender=WorkerType,
                               worker_type=worker_type)
        else:
            worker_offline.send(sender=WorkerType,
                                worker_type=worker_type)
