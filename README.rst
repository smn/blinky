Blinky
=============================

.. image:: https://img.shields.io/travis/smn/blinky.svg
        :target: https://travis-ci.org/smn/blinky

.. image:: https://img.shields.io/pypi/v/blinky.svg
        :target: https://pypi.python.org/pypi/blinky


Blinky provides uptime for Vumi workers & Junebug Channels

::

  docker run --rm -it \
    -e SUPERUSER_PASSWORD='password' \
    -e BROKER_URL='amqp://username:password@host/vhost' \
    -e DATABASE_URL='sqlite:////full/path/to/your/database/file.sqlite' \
    -p 8000:8000 \
    sdehaan/blinky
