from datetime import timedelta, datetime

import pytz

from django.test import TestCase
from django.utils import timezone
from .utils import BlinkMixin
from blinky.core.models import (
    System, WorkerInstance, WorkerType, HeartBeat, DAY)


class TestHeartBeat(BlinkMixin, TestCase):

    def test_ingest(self):
        self.assertFalse(System.objects.exists())
        self.assertFalse(WorkerType.objects.exists())
        self.assertFalse(WorkerInstance.objects.exists())
        self.assertFalse(HeartBeat.objects.exists())

        HeartBeat.ingest({
            'system_id': 'system_id',
            'hostname': 'hostname',
            'worker_name': 'worker_name',
            'pid': 1234,
            'timestamp': 1478373261.103398
        })

        HeartBeat.ingest({
            'system_id': 'system_id',
            'hostname': 'hostname',
            'worker_name': 'worker_name',
            'pid': 1234,
            'timestamp': 1478373335.093903
        })

        self.assertEqual(System.objects.count(), 1)
        self.assertEqual(WorkerType.objects.count(), 1)
        self.assertEqual(WorkerInstance.objects.count(), 1)
        self.assertEqual(HeartBeat.objects.count(), 2)

    def test_garbage_collect(self):
        heartbeat = self.mk_heartbeat()
        heartbeat.created_at = timezone.now() - timedelta(seconds=(1 * DAY))
        heartbeat.save()
        self.assertTrue(HeartBeat.objects.exists())
        HeartBeat.garbage_collect(gc_interval=(2 * DAY))
        self.assertTrue(HeartBeat.objects.exists())
        HeartBeat.garbage_collect(gc_interval=(1 * DAY), keep=1)
        self.assertTrue(HeartBeat.objects.exists())
        HeartBeat.garbage_collect(gc_interval=(1 * DAY), keep=0)
        self.assertFalse(HeartBeat.objects.exists())


class TestWorkerInstance(BlinkMixin, TestCase):

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.worker_instance.is_online())

    def test_offline(self):
        heartbeat = self.mk_heartbeat()
        worker_type = heartbeat.worker_type
        heartbeat.timestamp = (heartbeat.timestamp - timedelta(
            worker_type.heartbeat_interval + 1))
        heartbeat.save()
        self.assertFalse(heartbeat.worker_instance.is_online())

    def test_last_seen_at(self):
        now = datetime(2016, 11, 16, tzinfo=pytz.UTC)
        heartbeat = self.mk_heartbeat(timestamp=now)
        self.assertEqual(
            heartbeat.worker_instance.last_seen_at(), now)
        self.assertFalse(heartbeat.worker_instance.is_online())

    def test_online_with_timestamp(self):
        timestamp = timezone.now() - timedelta(days=1)
        timestamp_check = timestamp + timedelta(seconds=5)
        heartbeat = self.mk_heartbeat(timestamp=timestamp)
        worker_instance = heartbeat.worker_instance
        self.assertFalse(worker_instance.is_online())
        self.assertTrue(worker_instance.is_online(timestamp_check))


class TestWorkerType(BlinkMixin, TestCase):

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.worker_type.is_online())

    def test_instances_online(self):
        heartbeat = self.mk_heartbeat()
        worker_type = heartbeat.worker_type
        self.assertTrue(worker_type.is_online())

    def test_instances_instances_online(self):
        heartbeat1 = self.mk_heartbeat(hostname='host1')
        heartbeat2 = self.mk_heartbeat(hostname='host2')
        worker_type = heartbeat1.worker_type
        self.assertTrue(worker_type.is_online())
        self.assertEqual(
            set(worker_type.instances_online()),
            set([heartbeat1.worker_instance,
                 heartbeat2.worker_instance]))

    def test_capacity_good(self):
        system, worker_type = self.mk_system_capacity(online_count=1)
        worker_type.minimum_capacity = 0
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity(), WorkerType.CAPACITY_GOOD)

    def test_capacity_under(self):
        system, worker_type = self.mk_system_capacity(
            online_count=1, offline_count=4)
        worker_type.minimum_capacity = 5
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity(), WorkerType.CAPACITY_UNDER)

    def test_capacity_over(self):
        system, worker_type = self.mk_system_capacity(
            online_count=11, offline_count=0)
        worker_type.minimum_capacity = 1
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity(), WorkerType.CAPACITY_OVER)

    def test_capacity_at_timestamp(self):
        now = timezone.now()
        ten_seconds_ago = now - timedelta(
            seconds=WorkerType.DEFAULT_HEARTBEAT_INTERVAL)
        system, worker_type = self.mk_system_capacity(
            online_count=0, offline_count=1, offline_delta=1, now=now)
        self.assertEqual(worker_type.capacity(), WorkerType.CAPACITY_UNKNOWN)
        self.assertEqual(worker_type.capacity(ten_seconds_ago),
                         WorkerType.CAPACITY_GOOD)

    def test_last_seen_at(self):
        now = timezone.now()
        heartbeat1 = self.mk_heartbeat(timestamp=now - timedelta(seconds=1),
                                       hostname='hostname1')
        heartbeat2 = self.mk_heartbeat(timestamp=now - timedelta(seconds=2),
                                       hostname='hostname2')
        self.assertNotEqual(heartbeat1.worker_instance,
                            heartbeat2.worker_instance)
        self.assertEqual(heartbeat1.worker_type,
                         heartbeat1.worker_type)
        worker_type = heartbeat1.worker_type
        self.assertEqual(worker_type.last_seen_instance(),
                         heartbeat1.worker_instance)


class TestSystem(BlinkMixin, TestCase):

    def test_offline(self):
        system = self.mk_system()
        self.assertFalse(system.is_online())

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.system.is_online())

    def test_workertypes_online(self):
        heartbeat1 = self.mk_heartbeat(worker_name='worker1')
        heartbeat2 = self.mk_heartbeat(worker_name='worker2')
        system = heartbeat1.system
        self.assertTrue(
            set(system.workertypes_online()),
            set([heartbeat1.worker_type, heartbeat2.worker_type]))
