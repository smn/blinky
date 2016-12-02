from django.test import TestCase
from django.utils import timezone
from mock import Mock
from datetime import timedelta

from .utils import BlinkMixin
from ..models import WorkerType
from ..tasks import poll_worker_types


class TestSignals(BlinkMixin, TestCase):

    def test_worker_online(self):
        from ..signals import worker_online
        online_mock = Mock()
        worker_online.connect(online_mock)

        heartbeat = self.mk_heartbeat()
        heartbeat.timestamp = timezone.now() - timedelta(
            seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL * 2))
        heartbeat.save()

        heartbeat = self.mk_heartbeat()
        heartbeat.timestamp = timezone.now() - timedelta(
            seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL * 1))
        heartbeat.save()

        worker_type = heartbeat.worker_type
        worker_type.alive_beat_span = 1
        worker_type.status = WorkerType.STATUS_ONLINE
        worker_type.save()

        poll_worker_types()

        online_mock.assert_called_once_with(
            sender=WorkerType,
            worker_type=heartbeat.worker_type,
            signal=worker_online)

    def test_worker_offline(self):
        from ..signals import worker_offline
        offline_mock = Mock()
        worker_offline.connect(offline_mock)

        # Need to create two heartbeats because the signal handlers
        # need to have history to look at to determine a change in status
        heartbeat = self.mk_heartbeat()
        heartbeat.timestamp = (heartbeat.timestamp - timedelta(
            seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL * 3)))
        heartbeat.save()

        heartbeat = self.mk_heartbeat()
        heartbeat.timestamp = (heartbeat.timestamp - timedelta(
            seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL * 2)))
        heartbeat.save()

        poll_worker_types()

        offline_mock.assert_called_once_with(
            sender=WorkerType,
            worker_type=heartbeat.worker_type,
            signal=worker_offline)
