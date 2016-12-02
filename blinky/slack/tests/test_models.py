from django.test import TestCase
from blinky.core.tests.utils import BlinkMixin
from ..models import SlackWebhook


class SlackWebhookTest(BlinkMixin, TestCase):

    def test_for_worker_type_applied_global(self):
        system = self.mk_system()
        worker_type = self.mk_worker_type(system)

        wh = SlackWebhook(url='http://example.org', apply_global=True)
        wh.save()

        [found] = SlackWebhook.for_worker_type(worker_type)
        self.assertEqual(wh, found)

    def test_for_worker_type_limited_worker_type(self):
        system = self.mk_system()
        worker_type = self.mk_worker_type(system)

        wh = SlackWebhook(url='http://example.org', apply_global=False)
        wh.save()
        wh.limit_worker_types.add(worker_type)

        [found] = SlackWebhook.for_worker_type(worker_type)
        self.assertEqual(wh, found)

    def test_for_worker_type_limited_both_global_and_limited(self):
        system = self.mk_system()
        worker_type = self.mk_worker_type(system)

        wh = SlackWebhook(url='http://example.org', apply_global=True)
        wh.save()
        wh.limit_worker_types.add(worker_type)

        [found] = SlackWebhook.for_worker_type(worker_type)
        self.assertEqual(wh, found)

    def test_for_worker_type(self):
        system = self.mk_system()
        worker_type1 = self.mk_worker_type(system, worker_name='worker1')
        worker_type2 = self.mk_worker_type(system, worker_name='worker2')

        wh = SlackWebhook(url='http://example.org', apply_global=False)
        wh.save()
        wh.limit_worker_types.add(worker_type1)

        [found] = SlackWebhook.for_worker_type(worker_type1)
        self.assertEqual(wh, found)
        self.assertFalse(SlackWebhook.for_worker_type(worker_type2).exists())

    def test_for_worker_type_mixed(self):
        system = self.mk_system()
        worker_type1 = self.mk_worker_type(system, worker_name='worker1')
        worker_type2 = self.mk_worker_type(system, worker_name='worker2')

        wh1 = SlackWebhook(url='http://example.org', apply_global=False)
        wh1.save()
        wh1.limit_worker_types.add(worker_type1)

        wh2 = SlackWebhook(url='http://example.org', apply_global=True)
        wh2.save()

        self.assertEqual(
            SlackWebhook.for_worker_type(worker_type1).count(), 2)
        self.assertEqual(
            SlackWebhook.for_worker_type(worker_type2).count(), 1)
