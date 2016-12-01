from django.test import TestCase
from mock import Mock
from datetime import timedelta

from .utils import BlinkMixin
from ..models import WorkerType
from ..celery import poll_worker_types


class TestSignals(BlinkMixin, TestCase):

    def test_worker_online(self):
        from ..signals import worker_online
        online_mock = Mock()
        worker_online.connect(online_mock)

        heartbeat = self.mk_heartbeat()

        poll_worker_types()

        online_mock.assert_called_once_with(
            sender=WorkerType,
            worker_type=heartbeat.worker_type,
            signal=worker_online)

    def test_worker_offline(self):
        from ..signals import worker_offline
        offline_mock = Mock()
        worker_offline.connect(offline_mock)

        heartbeat = self.mk_heartbeat()
        heartbeat.timestamp = (heartbeat.timestamp - timedelta(
            seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL + 1)))
        heartbeat.save()

        poll_worker_types()

        offline_mock.assert_called_once_with(
            sender=WorkerType,
            worker_type=heartbeat.worker_type,
            signal=worker_offline)
