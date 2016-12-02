import responses
import json
from django.test import TestCase
from blinky.core.tests.utils import BlinkMixin
from blinky.core.models import WorkerType
from ..models import SlackWebhook
from ..signal_callbacks import (
    on_worker_online, on_worker_offline, on_worker_capacity_change)


class SignalCallbackTest(BlinkMixin, TestCase):

    def setUp(self):
        self.system = self.mk_system()
        self.worker_type = self.mk_worker_type(self.system)
        self.webhook = SlackWebhook(
            url='http://example.com/', channel='channel',
            username='username', icon_emoji='emoji')
        self.webhook.save()

    @responses.activate
    def test_on_worker_online(self):
        responses.add(responses.POST, 'http://example.com', body='{}')
        on_worker_online(None, self.worker_type)
        [call] = responses.calls
        data = json.loads(call.request.body)
        self.assertEqual(data, {
            "username": "username",
            "text": "worker_name came online.",
            "channel": "channel",
            "icon_emoji": "emoji",
        })

    @responses.activate
    def test_on_worker_offline(self):
        responses.add(responses.POST, 'http://example.com', body='{}')
        on_worker_offline(None, self.worker_type)
        [call] = responses.calls
        data = json.loads(call.request.body)
        self.assertEqual(data, {
            "username": "username",
            "text": "worker_name went offline.",
            "channel": "channel",
            "icon_emoji": "emoji",
        })

    @responses.activate
    def test_on_worker_capacity_changed(self):
        responses.add(responses.POST, 'http://example.com', body='{}')
        on_worker_capacity_change(
            None, self.worker_type,
            current_capacity=WorkerType.CAPACITY_GOOD,
            previous_capacity=WorkerType.CAPACITY_UNKNOWN)
        [call] = responses.calls
        data = json.loads(call.request.body)
        self.assertEqual(data, {
            "username": "username",
            "text": ("Capacity for worker_name changed from "
                     "CAPACITY_UNKNOWN to CAPACITY_GOOD."),
            "channel": "channel",
            "icon_emoji": "emoji",
        })
