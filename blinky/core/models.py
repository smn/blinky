from __future__ import unicode_literals

import pytz
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


class System(models.Model):
    system_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def workertypes_online(self, timestamp=None):
        return [worker_type
                for worker_type in self.workertype_set.filter(is_active=True)
                if worker_type.is_online(timestamp=timestamp)]

    def is_online(self, timestamp=None):
        return (
            self.workertype_set.filter(is_active=True).exists() and
            all(self.workertypes_online(timestamp=timestamp)))

    def __unicode__(self):
        return self.system_id


class WorkerType(models.Model):

    DEFAULT_HEARTBEAT_INTERVAL = 10 * SECOND
    CAPACITY_UNKNOWN = 'CAPACITY_UNKNOWN'
    CAPACITY_GOOD = 'CAPACITY_GOOD'
    CAPACITY_OVER = 'CAPACITY_OVER'
    CAPACITY_UNDER = 'CAPACITY_UNDER'
    STATUS_ONLINE = 'STATUS_ONLINE'
    STATUS_OFFLINE = 'STATUS_OFFLINE'
    STATUS_UNKNOWN = 'STATUS_UNKNOWN'

    system = models.ForeignKey(System)
    worker_friendly_name = models.TextField(null=True, blank=True)
    worker_name = models.CharField(max_length=255)
    heartbeat_interval = models.IntegerField(
        default=DEFAULT_HEARTBEAT_INTERVAL)
    created_at = models.DateTimeField(auto_now_add=True)
    minimum_capacity = models.IntegerField(default=0)
    maximum_capacity = models.IntegerField(default=10)
    alive_beat_span = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    status = models.CharField(default=STATUS_UNKNOWN, max_length=255, choices=(
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_ONLINE, 'Online'),
        (STATUS_UNKNOWN, 'Unknown'),
    ))

    def last_seen_instance(self):
        return max(self.workerinstance_set.all(),
                   key=lambda instance: instance.last_seen_at())

    def instances_online(self, timestamp=None):
        return [worker_instance
                for worker_instance in self.workerinstance_set.all()
                if worker_instance.is_online(timestamp=timestamp)]

    def instances_offline(self, timestamp=None):
        return [worker_instance
                for worker_instance in self.workerinstance_set.all()
                if not worker_instance.is_online(timestamp=timestamp)]

    def is_alive(self, timestamp=None, beats=None):
        beats = beats or self.alive_beat_span
        until = timestamp or timezone.now()
        since = until - timedelta(
            seconds=(self.heartbeat_interval * beats))
        beats_found = self.heartbeat_set.filter(timestamp__lte=until,
                                                timestamp__gte=since).count()
        return beats_found >= beats

    def is_online(self, timestamp=None):
        return any(self.instances_online(timestamp=timestamp))

    def capacity(self, timestamp=None):
        instance_count = len(self.instances_online(timestamp))
        if not instance_count:
            return self.CAPACITY_UNKNOWN
        if self.minimum_capacity <= instance_count <= self.maximum_capacity:
            return self.CAPACITY_GOOD
        elif instance_count < self.minimum_capacity:
            return self.CAPACITY_UNDER
        elif instance_count > self.maximum_capacity:
            return self.CAPACITY_OVER

    @classmethod
    def garbage_collect(cls, gc_interval=(1 * MINUTE), now=None):
        now = now or timezone.now()
        for worker_type in cls.objects.all():
            last_instance = worker_type.last_seen_instance()
            delta = last_instance.last_seen_at() - now
            worker_type.is_active = (
                abs(delta.total_seconds()) < float(gc_interval))
            worker_type.save()

    def __unicode__(self):
        return self.worker_friendly_name or self.worker_name


class WorkerInstance(models.Model):
    worker_type = models.ForeignKey(WorkerType)
    hostname = models.CharField(max_length=255)
    pid = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def last_seen_at(self):
        try:
            return self.heartbeat_set.latest().timestamp
        except (HeartBeat.DoesNotExist,):
            return None

    def is_on_time(self, heartbeat, timestamp=None):
        timestamp = timestamp or timezone.now()
        last_interval = (heartbeat.timestamp - timestamp).total_seconds()
        return abs(last_interval) < self.worker_type.heartbeat_interval

    def is_online(self, timestamp=None):
        """
        Check whether or not a WorkerInstance is online.
        If a timestamp is given, check whether the WorkerInstance was online
        at the given time.

        :param timestamp datetime: Optional timestamp
        :returns: bool
        """
        timestamp = timestamp or timezone.now()
        queryset = self.heartbeat_set.all()
        if timestamp:
            queryset = queryset.filter(timestamp__lt=timestamp)

        if not queryset.exists():
            return False

        return self.is_on_time(queryset.latest(), timestamp)

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
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def previous(self):
        return HeartBeat.objects.filter(
            system=self.system, worker_type=self.worker_type,
            worker_instance=self.worker_instance,
            timestamp__lt=self.timestamp).order_by('-timestamp').first()

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

    @classmethod
    def garbage_collect(cls, gc_interval=(14 * DAY), keep=10, now=None):
        now = now or timezone.now()
        cut_off = now - timedelta(seconds=gc_interval)
        heartbeats = cls.objects.filter(created_at__lte=cut_off)
        recent_100 = heartbeats.values_list('pk', flat=True)[:keep]
        return heartbeats.exclude(pk__in=recent_100).delete()

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
