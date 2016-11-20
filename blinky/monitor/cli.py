import os
import click
import pika
from pika.exceptions import ConnectionClosed
from urlparse import urlparse, urlunparse
from urllib import quote_plus
import json
import re


def quote_vhost(broker_url):
    """
    NOTE:   The only reason this is needed is because the Pika library wants
            the vhost section of the broker URL to be quoted so a leading
            slash on a `/vhost` needs to be quoted as `'%2Fvhost`.
    """
    parse = urlparse(broker_url)
    return urlunparse((
        parse.scheme,
        parse.netloc,
        '/%s' % quote_plus(re.sub(r'^/', '', parse.path)),
        parse.params,
        parse.query,
        parse.fragment
    ))


@click.command()
@click.option('--broker-url',
              default='amqp://guest:guest@localhost/', envvar='BROKER_URL',
              type=quote_vhost)
@click.option('--settings', default='blinky.settings')
@click.option('--queue-name', default='heartbeat.inbound')
@click.option('--exchange', default='vumi.health')
@click.option('--verbose/--no-verbose', default=False)
def run(broker_url, settings, queue_name, exchange, verbose):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

    import django
    from django.conf import settings
    django.setup()

    from blinky.core.models import HeartBeat

    parameters = pika.URLParameters(broker_url)

    try:
        connection = pika.BlockingConnection(parameters)
    except (ConnectionClosed,) as e:
        raise click.ClickException('Unable to connect to AMQP: %r' % e)

    channel = connection.channel()
    channel.exchange_declare(exchange=exchange,
                             type='direct',
                             durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange,
                       queue=queue_name)

    def callback(ch, method, properties, body):
        heartbeat = HeartBeat.ingest(json.loads(body))
        if verbose:
            click.echo('<3 from %s at %s.' % (
                heartbeat.worker_instance,
                heartbeat.timestamp.isoformat()))

    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)
    try:
        channel.start_consuming()
    except (ConnectionClosed,) as e:
        raise click.ClickException('Lost Connection to AMQP: %r' % e)
    except (KeyboardInterrupt,) as e:
        connection.close()
