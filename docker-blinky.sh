#/bin/bash -e

django-admin collectstatic --noinput --settings=blinky.settings
django-admin migrate --noinput --settings=blinky.settings

if [ -n "$SUPERUSER_PASSWORD" ]; then
  echo "from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '$SUPERUSER_PASSWORD')
" | su-exec gunicorn django-admin shell
  echo "Created superuser with username 'admin' and password '$SUPERUSER_PASSWORD'"
fi

exec gunicorn --bind 0.0.0.0:8000 blinky.wsgi
