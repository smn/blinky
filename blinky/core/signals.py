from django.dispatch import Signal


worker_instance_online = Signal(providing_args=["worker_instance"])
worker_instance_offline = Signal(providing_args=["worker_instance"])
