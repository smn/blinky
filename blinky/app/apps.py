from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        print 'hi!'
        from .signal_callbacks import post_save_heartbeat
        post_save.connect(
            post_save_heartbeat,
            sender='app.HeartBeat')
