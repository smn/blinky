from __future__ import unicode_literals
import requests

from django.db import models


class SlackWebhook(models.Model):
    url = models.URLField()
    username = models.CharField(max_length=255, null=True, blank=True)
    icon_emoji = models.CharField(max_length=255, null=True, blank=True)
    channel = models.CharField(max_length=255, null=True, blank=True)
    apply_global = models.BooleanField(default=True)
    limit_worker_types = models.ManyToManyField('core.WorkerType', blank=True)

    @classmethod
    def for_worker_type(cls, worker_type):
        return cls.objects.filter(
            models.Q(apply_global=True) |
            models.Q(limit_worker_types=worker_type)
        ).distinct()

    def slack_payload(self, text):
        payload = {
            'text': text
        }
        if self.username:
            payload['username'] = self.username
        if self.icon_emoji:
            payload['icon_emoji'] = self.icon_emoji
        if self.channel:
            payload['channel'] = self.channel
        return payload

    def fire(self, text):
        response = requests.post(self.url, headers={
            'Content-Type': 'application/json',
        }, json=self.slack_payload(text))
        response.raise_for_status()
        return response.json()
