import logging

from django.contrib import admin

from telegram_bot.models import User, ScheduledTask
from wireguard.exceptions import VPNServerError
from wireguard.services.vpn_server import VPNServerService
from wireguard.tasks import on_user_subscription_date_updated


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    pass


class UserInline(admin.TabularInline):
    model = User
    extra = False
    classes = ('collapse',)
    can_delete = False
    show_change_link = True
    readonly_fields = ('is_subscribed',)
    ordering = ('-registered_at',)

    @admin.display(boolean=True)
    def is_subscribed(self, obj):
        return obj.is_subscribed

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = (
        'is_subscribed',
        'has_activated_promocode',
        'telegram_id',
        'uuid',
        'is_trial_period',
        'registered_at',
    )
    search_fields = ('telegram_id',)
    search_help_text = 'User Telegram ID'
    autocomplete_fields = ('server',)

    @admin.display(boolean=True)
    def is_subscribed(self, obj):
        return obj.is_subscribed

    def save_model(self, request, obj, form, change):
        old_user: User = self.model.objects.filter(id=obj.id).select_related('server').first()
        if old_user is not None and obj.subscribed_at != old_user.subscribed_at:
            on_user_subscription_date_updated.delay(telegram_id=obj.telegram_id)
        if obj.server.url != old_user.server.url:
            if old_user is not None:
                try:
                    with VPNServerService(base_url=old_user.server.url,
                                          password=old_user.server.password) as old_vpn_server:
                        old_vpn_server.login()
                        old_vpn_server.delete_user(old_user.uuid)
                except VPNServerError:
                    logging.error('Could not delete user from old server')
            try:
                with VPNServerService(base_url=obj.server.url, password=obj.server.password) as new_vpn_server:
                    new_vpn_server.login()
                    user_in_vpn_server, _ = new_vpn_server.get_or_create_user(obj.telegram_id)
            except VPNServerError:
                logging.error('Could not create user in new server')
            else:
                obj.uuid = user_in_vpn_server.uuid
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        try:
            with VPNServerService(base_url=obj.server.url, password=obj.server.password) as old_vpn_server:
                old_vpn_server.login()
                old_vpn_server.delete_user(obj.uuid)
        except VPNServerError:
            logging.error('Could not delete user in server')
        super().delete_model(request, obj)

    def has_add_permission(self, request):
        return False
