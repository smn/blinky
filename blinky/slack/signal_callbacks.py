from .models import SlackWebhook


def on_worker_online(sender, worker_type, **kwargs):
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('%s came online.' % (worker_type,))


def on_worker_offline(sender, worker_type, **kwargs):
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('%s went offline.' % (worker_type,))


def on_worker_capacity_change(sender, worker_type, previous_capacity,
                              current_capacity, **kwargs):
    for webhook in SlackWebhook.for_worker_type(worker_type):
        webhook.fire('Capacity for %s changed from %s to %s.' % (
            worker_type, previous_capacity, current_capacity))
