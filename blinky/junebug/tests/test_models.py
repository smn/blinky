import responses
from django.test import TestCase
from blinky.core.tests.utils import BlinkMixin, reload_record
from ..models import JunebugInstance
from ..tasks import update_workers_junebug_info


class JunebugTestCase(BlinkMixin, TestCase):

    def setUp(self):
        self.junebug = JunebugInstance.objects.create(url='http://junebug')
        responses.add(
            responses.GET,
            'http://junebug/channels/',
            json={
                "status": 200,
                "code": "OK",
                "description": "channels listed",
                "result": [
                    "099059cb-3f71-488e-9b02-126de798e8e2",
                    "378740d2-b043-4c82-9316-b9586f8c57dc",
                ]
            })
        responses.add(
            responses.GET,
            'http://junebug/channels/099059cb-3f71-488e-9b02-126de798e8e2',
            json={
                "status": 200,
                "code": "OK",
                "description": "channel found",
                "result": {
                    "label": "A channel with a label",
                    "amqp_queue": "amqp-queue-1",
                    "type": "vumigo",
                    "id": "099059cb-3f71-488e-9b02-126de798e8e2"
                }
            })
        responses.add(
            responses.GET,
            'http://junebug/channels/378740d2-b043-4c82-9316-b9586f8c57dc',
            json={
                "status": 200,
                "code": "OK",
                "description": "channel found",
                "result": {
                    "amqp_queue": "amqp-queue-1",
                    "mo_url": "http://example.com",
                    "type": "vumigo",
                    "id": "378740d2-b043-4c82-9316-b9586f8c57dc"
                }
            })

    def test_format_channel_name_with_id(self):
        jb = JunebugInstance()
        self.assertEqual(
            jb.format_channel_name({
                'id': 'foo',
                'amqp_queue': 'amqp_queue',
                'mo_url': 'mo_url',
                'type': 'channel_type'
            }),
            'foo of type channel_type on Queue amqp_queue / MO URL: mo_url')

    def test_format_channel_name_with_label(self):
        jb = JunebugInstance()
        self.assertEqual(
            jb.format_channel_name({
                'id': 'foo',
                'label': 'bar',
                'amqp_queue': 'amqp_queue',
                'mo_url': 'mo_url',
                'type': 'channel_type',
            }),
            ('bar (foo) of type channel_type on Queue '
             'amqp_queue / MO URL: mo_url'))

    @responses.activate
    def test_get_channels(self):
        [channel1, channel2] = self.junebug.get_channels()
        self.assertEqual(
            channel1['id'], '099059cb-3f71-488e-9b02-126de798e8e2')
        self.assertEqual(
            channel2['id'], '378740d2-b043-4c82-9316-b9586f8c57dc')
        self.assertEqual(len(responses.calls), 3)

    @responses.activate
    def test_task(self):
        system = self.mk_system()
        worker = self.mk_worker_type(
            system,
            worker_name='099059cb-3f71-488e-9b02-126de798e8e2')
        self.assertEqual(reload_record(worker).worker_friendly_name, None)
        update_workers_junebug_info(workertype_pk=worker.pk)
        self.assertEqual(
            reload_record(worker).worker_friendly_name,
            ('A channel with a label (099059cb-3f71-488e-9b02-126de798e8e2) '
             'of type vumigo on Queue amqp-queue-1 / MO URL: None'))
