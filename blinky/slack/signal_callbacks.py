from .models import SlackWebhook
from django.contrib.sites.models import Site


def on_worker_online(sender, worker_type, **kwargs):
    site = Site.objects.get_current()
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('<http://%s%s|%s> came online.' % (
            site.domain, worker_type.get_absolute_url(), worker_type,))


def on_worker_offline(sender, worker_type, **kwargs):
    site = Site.objects.get_current()
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('<http://%s%s|%s> went offline.' % (
            site.domain, worker_type.get_absolute_url(), worker_type,))


def on_worker_capacity_change(sender, worker_type, previous_capacity,
                              current_capacity, **kwargs):
    site = Site.objects.get_current()
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('Capacity for <http://%s%s|%s> changed from %s to %s.' % (
            site.domain, worker_type.get_absolute_url(), worker_type,
            previous_capacity, current_capacity))
