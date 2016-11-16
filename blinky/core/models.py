from __future__ import unicode_literals

import pytz
from django.db import models
from datetime import datetime
from django.utils import timezone


class System(models.Model):
    system_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def workertypes_online(self):
        return [worker_type
                for worker_type in self.workertype_set.filter(is_active=True)
                if worker_type.online]

    @property
    def online(self):
        return (
            self.workertype_set.filter(is_active=True).exists() and
            all(self.workertypes_online))

    def __unicode__(self):
        return self.system_id


class WorkerType(models.Model):

    DEFAULT_HEARTBEAT_INTERVAL = 10
    CAPACITY_GOOD = 'CAPACITY_GOOD'
    CAPACITY_OVER = 'CAPACITY_OVER'
    CAPACITY_UNDER = 'CAPACITY_UNDER'

    system = models.ForeignKey(System)
    worker_name = models.CharField(max_length=255)
    heartbeat_interval = models.IntegerField(
        default=DEFAULT_HEARTBEAT_INTERVAL)
    created_at = models.DateTimeField(auto_now_add=True)
    minimum_capacity = models.IntegerField(default=0)
    maximum_capacity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    @property
    def last_seen_instance(self):
        return max(self.workerinstance_set.all(),
                   key=lambda instance: instance.last_seen_at)

    @property
    def instances_online(self):
        return [worker_instance
                for worker_instance in self.workerinstance_set.all()
                if worker_instance.online]

    @property
    def instances_offline(self):
        return [worker_instance
                for worker_instance in self.workerinstance_set.all()
                if not worker_instance.online]

    @property
    def online(self):
        return any(self.instances_online)

    @property
    def capacity(self):
        instance_count = len(self.instances_online)
        if self.minimum_capacity <= instance_count <= self.maximum_capacity:
            return self.CAPACITY_GOOD
        elif instance_count < self.minimum_capacity:
            return self.CAPACITY_UNDER
        elif instance_count > self.maximum_capacity:
            return self.CAPACITY_OVER

    @classmethod
    def garbage_collect(cls, gc_interval=60, now=None):
        now = now or timezone.now()
        for worker_type in WorkerType.objects.all():
            last_instance = worker_type.last_seen_instance
            delta = last_instance.last_seen_at - now
            worker_type.is_active = (
                abs(delta.total_seconds()) < float(gc_interval))
            worker_type.save()

    def __unicode__(self):
        return self.worker_name


class WorkerInstance(models.Model):
    worker_type = models.ForeignKey(WorkerType)
    hostname = models.CharField(max_length=255)
    pid = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def last_seen_at(self):
        return self.heartbeat_set.latest().timestamp

    @property
    def online(self):
        last_interval = (self.heartbeat_set.latest().timestamp -
                         timezone.now()).total_seconds()
        return abs(last_interval) < self.worker_type.heartbeat_interval

    def __unicode__(self):
        return u'%s:%s @ %s with pid %s' % (
            self.worker_type.system,
            self.worker_type,
            self.hostname,
            self.pid)


class HeartBeat(models.Model):
    system = models.ForeignKey(System)
    worker_type = models.ForeignKey(WorkerType)
    worker_instance = models.ForeignKey(WorkerInstance)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    @classmethod
    def ingest(cls, data):
        system, _ = System.objects.get_or_create(
            system_id=data['system_id'])
        worker_type, _ = WorkerType.objects.get_or_create(
            system=system,
            worker_name=data['worker_name'])
        worker_instance, _ = WorkerInstance.objects.get_or_create(
            worker_type=worker_type,
            hostname=data['hostname'],
            pid=data['pid'])
        return cls.objects.create(
            system=system,
            worker_type=worker_type,
            worker_instance=worker_instance,
            timestamp=datetime.fromtimestamp(
                data['timestamp']).replace(tzinfo=pytz.UTC))

    def __unicode__(self):
        return u'%s @ %s' % (self.worker_instance, self.timestamp.isoformat())


class WorkerLog(models.Model):
    worker_type = models.ForeignKey(WorkerType)
    heartbeat = models.ForeignKey(HeartBeat)
    message = models.TextField()
    level = models.CharField(max_length=255, choices=(
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('debug', 'Debug'),
    ))
