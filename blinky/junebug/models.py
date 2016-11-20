from __future__ import unicode_literals

from django.db import models
import requests


class JunebugInstance(models.Model):
    url = models.URLField()
    username = models.CharField(null=True, blank=True, max_length=255)
    password = models.CharField(null=True, blank=True, max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_channels(self):
        response = requests.get(
            '%s/channels/' % (self.url,),
            auth=(self.username, self.password))
        response.raise_for_status()
        channels_list = response.json()
        for uuid in channels_list['result']:
            response = requests.get('%s/channels/%s' % (self.url, uuid))
            yield response.json()['result']

    def format_channel_name(self, channel):
        label = channel.get('label')
        if label:
            name = '%s (%s)' % (label, channel.get('id'))
        else:
            name = channel.get('id')

        return '%s of type %s on Queue %s / MO URL: %s' % (
            name, channel.get('type'),
            channel.get('amqp_queue'), channel.get('mo_url'))

    def __str__(self):
        return self.url
