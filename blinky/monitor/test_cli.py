from django.test import TestCase
from .cli import quote_vhost


class CliTestCase(TestCase):

    def test_quote_vhost_without_slash(self):
        self.assertEqual(
            quote_vhost('amqp://guest:guest@localhost/foo'),
            'amqp://guest:guest@localhost/foo')

    def test_quote_vhost_with_slash(self):
        self.assertEqual(
            quote_vhost('amqp://guest:guest@localhost//foo'),
            'amqp://guest:guest@localhost/%2Ffoo')
