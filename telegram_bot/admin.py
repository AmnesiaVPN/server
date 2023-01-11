from django.contrib import admin

from telegram_bot.models import User
from wireguard.services import vpn_server


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('registered_at',)
    search_fields = ('telegram_id',)
    search_help_text = 'User Telegram ID'

    def save_model(self, request, obj, form, change):
        server = obj.server
        with vpn_server.connected_client(server.url, server.password) as client:
            user = vpn_server.get_or_create_user(client, str(obj.telegram_id))
        obj.uuid = user.uuid
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
