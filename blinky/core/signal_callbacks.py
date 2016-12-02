from .signals import worker_capacity_change


def post_save_heartbeat(sender, instance, created, **kwargs):
    previous_heartbeat = instance.previous()
    if not previous_heartbeat:
        return

    timestamp = previous_heartbeat.timestamp

    worker_type = instance.worker_type
    current_capacity = worker_type.capacity()
    previous_capacity = worker_type.capacity(timestamp)
    if current_capacity != previous_capacity:
        worker_capacity_change.send(sender=worker_type.__class__,
                                    worker_type=worker_type,
                                    current_capacity=current_capacity,
                                    previous_capacity=previous_capacity)
