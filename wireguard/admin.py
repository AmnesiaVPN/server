from django.contrib import admin

from wireguard.models import Server
from telegram_bot.admin import UserInline


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    inlines = (UserInline,)
    search_fields = ('name', 'url')
