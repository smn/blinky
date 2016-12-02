from django.contrib import admin
from .models import SlackWebhook


@admin.register(SlackWebhook)
class SlackWebhookAdmin(admin.ModelAdmin):
    pass
