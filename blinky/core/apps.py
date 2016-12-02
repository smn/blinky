from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save


class CoreAppConfig(AppConfig):
    name = 'blinky.core'

    def ready(self):
        from .signal_callbacks import (
            post_save_heartbeat, pre_save_worker_type)
        post_save.connect(post_save_heartbeat, sender='core.HeartBeat')
        pre_save.connect(pre_save_worker_type, sender='core.WorkerType')
