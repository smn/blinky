from django.test import TestCase
from mock import Mock

from .utils import BlinkMixin
from ..models import WorkerType
from ..tasks import poll_worker_types


class TestSignals(BlinkMixin, TestCase):

    def test_worker_online(self):
        from ..signals import worker_online
        online_mock = Mock()
        worker_online.connect(online_mock)

        heartbeat = self.mk_heartbeat()
        heartbeat = self.mk_heartbeat()

        worker_type = heartbeat.worker_type
        worker_type.alive_beat_span = 2
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

        # 1 heartbeat
        heartbeat = self.mk_heartbeat()

        # 2 heartbeats needed to be alive
        worker_type = heartbeat.worker_type
        worker_type.alive_beat_span = 2
        worker_type.save()

        poll_worker_types()

        offline_mock.assert_called_once_with(
            sender=WorkerType,
            worker_type=heartbeat.worker_type,
            signal=worker_offline)
