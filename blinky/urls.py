"""blinky URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from blinky.core.views import (
    WorkerTypeList, WorkerInstanceList, HeartBeatList)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.login, {
        'template_name': 'core/login.html',
    }, name='login'),
    url(r'^$',
        login_required(WorkerTypeList.as_view()), name='workertypes'),
    url(r'^workertype/(?P<workertype_pk>\d+)/$',
        login_required(WorkerInstanceList.as_view()), name='workerinstances'),
    url(r'^workertype/(?P<workertype_pk>\d+)/(?P<workerinstance_pk>\d+)/$',
        login_required(HeartBeatList.as_view()), name='heartbeats'),
]
