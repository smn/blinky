from django.test import TestCase
from blinky.app.models import System, Worker, HeartBeat


class TestHeartBeat(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ingest(self):
        self.assertFalse(System.objects.exists())
        self.assertFalse(Worker.objects.exists())
        self.assertFalse(HeartBeat.objects.exists())

        HeartBeat.ingest({
            'system_id': 'system_id',
            'hostname': 'hostname',
            'worker_name': 'worker_name',
            'pid': 1234,
            'timestamp': 1478373261.103398
        })

        HeartBeat.ingest({
            'system_id': 'system_id',
            'hostname': 'hostname',
            'worker_name': 'worker_name',
            'pid': 1234,
            'timestamp': 1478373335.093903
        })

        self.assertEqual(System.objects.count(), 1)
        self.assertEqual(Worker.objects.count(), 1)
        self.assertEqual(HeartBeat.objects.count(), 2)

    def test_status_change(self):
        pass
