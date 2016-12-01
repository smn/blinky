from blinky.core import celery_app as app
from django.contrib.auth.models import User


@app.task
def health_check():
    print 'hullo'
    return User.objects.all().count()
