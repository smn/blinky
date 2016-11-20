#/bin/bash -e

sleep 5

exec python -m blinky.monitor --verbose --settings=blinky.settings
