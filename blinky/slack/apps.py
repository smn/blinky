from __future__ import unicode_literals

from django.apps import AppConfig


class SlackConfig(AppConfig):
    name = 'blinky.slack'

    def ready(self):
        from blinky.core.signals import (
            worker_online, worker_offline, worker_capacity_change)
        from . import signal_callbacks
        print 'slack signals!'
        worker_online.connect(signal_callbacks.on_worker_online)
        worker_offline.connect(signal_callbacks.on_worker_offline)
        worker_capacity_change.connect(
            signal_callbacks.on_worker_capacity_change)
        print 'done!'
