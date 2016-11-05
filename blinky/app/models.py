from __future__ import unicode_literals

import pytz
from django.db import models
from datetime import datetime


class System(models.Model):
    system_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.system_id


class Worker(models.Model):
    system = models.ForeignKey(System)
    worker_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.worker_name


class HeartBeat(models.Model):
    system = models.ForeignKey(System)
    worker = models.ForeignKey(Worker)
    timestamp = models.DateTimeField()
    hostname = models.CharField(max_length=255, null=True)
    pid = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    @classmethod
    def ingest(cls, data):
        system, _ = System.objects.get_or_create(
            system_id=data['system_id'])
        worker, _ = Worker.objects.get_or_create(
            system=system,
            worker_name=data['worker_name'])
        return cls.objects.create(
            system=system,
            worker=worker,
            hostname=data['hostname'],
            pid=data['pid'],
            timestamp=datetime.fromtimestamp(
                data['timestamp']).replace(tzinfo=pytz.UTC))

    def __unicode__(self):
        return u'%s @ %s' % (self.worker, self.timestamp.isoformat())
