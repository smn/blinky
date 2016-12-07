from django.test import TestCase
from django.core.urlresolvers import reverse
from blinky.core.tests.utils import BlinkMixin


class WorkerHealthTest(BlinkMixin, TestCase):

    def test_health_bad(self):
        system, worker_type = self.mk_system_capacity(
            online_count=0, offline_count=4)
        worker_type.save()
        url = reverse('workertypehealth', kwargs={
            'workertype_pk': worker_type.pk,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_health_good(self):
        system, worker_type = self.mk_system_capacity(
            online_count=1, offline_count=0)
        worker_type.save()
        url = reverse('workertypehealth', kwargs={
            'workertype_pk': worker_type.pk,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
