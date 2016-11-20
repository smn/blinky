from datetime import timedelta
from django.utils import timezone
from blinky.core.models import (
    System, WorkerInstance, WorkerType, HeartBeat)


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
