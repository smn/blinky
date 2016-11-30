from django.dispatch import Signal


worker_online = Signal(providing_args=["worker_type"])
worker_offline = Signal(providing_args=["worker_type"])
worker_capacity_change = Signal(providing_args=["worker_type", "capacity"])
