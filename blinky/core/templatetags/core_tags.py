from django import template
from django.utils import timezone

register = template.Library()


@register.filter()
def was_on_time(heartbeat):
    next_heartbeat = heartbeat.next()
    if next_heartbeat is None:
        timestamp = timezone.now()
    else:
        timestamp = next_heartbeat.timestamp
    return heartbeat.is_on_time(timestamp)
