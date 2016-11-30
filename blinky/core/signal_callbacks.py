from .signals import worker_capacity_change


def post_save_heartbeat(sender, instance, created, **kwargs):
    previous_heartbeat = instance.previous()
    if not previous_heartbeat:
        return

    timestamp = previous_heartbeat.timestamp
    worker_type = instance.worker_type

    current_capacity = worker_type.capacity()
    if current_capacity != worker_type.capacity(timestamp):
        worker_capacity_change.send(sender=worker_type.__class__,
                                    worker_type=worker_type,
                                    capacity=current_capacity)
