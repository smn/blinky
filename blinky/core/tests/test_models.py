from datetime import timedelta, datetime

import pytz

from django.test import TestCase
from django.utils import timezone
from blinky.core.models import (
    System, WorkerInstance, WorkerType, HeartBeat, DAY)


def reload_record(record):
    return record.__class__.objects.get(pk=record.pk)


class BlinkMixin(object):

    def mk_system(self, system_id='system_id'):
        system, _ = System.objects.get_or_create(system_id=system_id)
        return system

    def mk_worker_type(self, system, worker_name='worker_name',
                       heartbeat_interval=10):
        worker_type, _ = WorkerType.objects.get_or_create(
            system=system, worker_name=worker_name,
            heartbeat_interval=heartbeat_interval)
        return worker_type

    def mk_worker_instance(self, worker_type, hostname='hostname', pid=1234):
        worker_instance, _ = WorkerInstance.objects.get_or_create(
            worker_type=worker_type,
            hostname=hostname,
            pid=pid)
        return worker_instance

    def mk_heartbeat(self, system_id='system_id', hostname='hostname',
                     worker_name='worker_name', pid=1234,
                     heartbeat_interval=10, timestamp=None):
        timestamp = timestamp or timezone.now()
        system = self.mk_system(system_id)
        worker_type = self.mk_worker_type(
            system, worker_name,
            heartbeat_interval=heartbeat_interval)
        worker_instance = self.mk_worker_instance(
            worker_type, hostname=hostname, pid=pid)
        heartbeat, _ = HeartBeat.objects.get_or_create(
            system=system, worker_type=worker_type,
            worker_instance=worker_instance, timestamp=timestamp)
        return heartbeat

    def mk_system_capacity(self, online_count=0, offline_count=0):
        system = self.mk_system()
        for online_worker in range(online_count):
            heartbeat = self.mk_heartbeat(system_id=system.system_id,
                                          hostname='online-host-%s' % (
                                              online_worker))

        for offline_worker in range(offline_count):
            seconds_ago = timezone.now() - timedelta(
                seconds=(WorkerType.DEFAULT_HEARTBEAT_INTERVAL +
                         offline_worker + 1))
            heartbeat = self.mk_heartbeat(system_id=system.system_id,
                                          hostname='offline-host-%s' % (
                                              offline_worker),
                                          timestamp=seconds_ago)
        return (system, heartbeat.worker_type)


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
        HeartBeat.garbage_collect(gc_interval=(1 * DAY))
        self.assertFalse(HeartBeat.objects.exists())


class TestWorkerInstance(BlinkMixin, TestCase):

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.worker_instance.online)

    def test_offline(self):
        heartbeat = self.mk_heartbeat()
        worker_type = heartbeat.worker_type
        heartbeat.timestamp = (heartbeat.timestamp - timedelta(
            worker_type.heartbeat_interval + 1))
        heartbeat.save()
        self.assertFalse(heartbeat.worker_instance.online)

    def test_last_seen_at(self):
        now = datetime(2016, 11, 16, tzinfo=pytz.UTC)
        heartbeat = self.mk_heartbeat(timestamp=now)
        self.assertEqual(
            heartbeat.worker_instance.last_seen_at, now)
        self.assertFalse(heartbeat.worker_instance.online)


class TestWorkerType(BlinkMixin, TestCase):

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.worker_type.online)

    def test_instances_online(self):
        heartbeat = self.mk_heartbeat()
        worker_type = heartbeat.worker_type
        self.assertTrue(worker_type.online)

    def test_instances_instances_online(self):
        heartbeat1 = self.mk_heartbeat(hostname='host1')
        heartbeat2 = self.mk_heartbeat(hostname='host2')
        worker_type = heartbeat1.worker_type
        self.assertTrue(worker_type.online)
        self.assertEqual(
            set(worker_type.instances_online),
            set([heartbeat1.worker_instance,
                 heartbeat2.worker_instance]))

    def test_capacity_good(self):
        system, worker_type = self.mk_system_capacity(online_count=1)
        worker_type.minimum_capacity = 0
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity, WorkerType.CAPACITY_GOOD)

    def test_capacity_under(self):
        system, worker_type = self.mk_system_capacity(
            online_count=1, offline_count=4)
        worker_type.minimum_capacity = 5
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity, WorkerType.CAPACITY_UNDER)

    def test_capacity_over(self):
        system, worker_type = self.mk_system_capacity(
            online_count=11, offline_count=0)
        worker_type.minimum_capacity = 1
        worker_type.maximum_capacity = 10
        worker_type.save()
        self.assertEqual(worker_type.capacity, WorkerType.CAPACITY_OVER)

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
        self.assertEqual(worker_type.last_seen_instance,
                         heartbeat1.worker_instance)

    def test_garbage_collect_remain_active(self):
        system, worker_type = self.mk_system_capacity(online_count=1)
        self.assertTrue(worker_type.is_active)
        WorkerType.garbage_collect()
        self.assertTrue(reload_record(worker_type).is_active)

    def test_garbage_collect_flip_in_active(self):
        system, worker_type = self.mk_system_capacity(offline_count=1)
        self.assertTrue(worker_type.is_active)
        WorkerType.garbage_collect(gc_interval=10)
        self.assertFalse(reload_record(worker_type).is_active)


class TestSystem(BlinkMixin, TestCase):

    def test_offline(self):
        system = self.mk_system()
        self.assertFalse(system.online)

    def test_online(self):
        heartbeat = self.mk_heartbeat()
        self.assertTrue(heartbeat.system.online)

    def test_workertypes_online(self):
        heartbeat1 = self.mk_heartbeat(worker_name='worker1')
        heartbeat2 = self.mk_heartbeat(worker_name='worker2')
        system = heartbeat1.system
        self.assertTrue(
            set(system.workertypes_online),
            set([heartbeat1.worker_type, heartbeat2.worker_type]))
