from __future__ import unicode_literals

import pytz
from django.db import models
from datetime import datetime


class System(models.Model):
    system_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.system_id


class WorkerType(models.Model):
    system = models.ForeignKey(System)
    worker_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.worker_name


class WorkerInstance(models.Model):
    worker_type = models.ForeignKey(WorkerType)
    hostname = models.CharField(max_length=255)
    pid = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s:%s @ %s with pid %s' % (
            self.worker_type.system,
            self.worker_type,
            self.hostname,
            self.pid)


class HeartBeat(models.Model):
    system = models.ForeignKey(System)
    worker_type = models.ForeignKey(WorkerType)
    worker_instance = models.ForeignKey(WorkerInstance, null=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

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
