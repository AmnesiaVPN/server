import httpx
from django.contrib import admin, messages

from telegram_bot.admin import UserInline
from wireguard.exceptions import VPNServerError
from wireguard.models import Server
from wireguard.services.vpn_server import VPNServerService


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    inlines = (UserInline,)
    search_fields = ('name', 'url')

    def save_model(self, request, obj: Server, form, change):
        with VPNServerService(base_url=obj.url, password=obj.password) as vpn_server:
            try:
                vpn_server.login()
            except (VPNServerError, httpx.ConnectError):
                # as we can't disable 'success message' on each model save, we can just change log level
                messages.set_level(request, level=messages.ERROR)
                messages.error(request, f'Invalid server url {obj.url} or password {obj.password}')
            else:
                super().save_model(request, obj, form, change)
