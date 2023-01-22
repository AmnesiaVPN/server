import logging

from django.contrib import admin
from django.db.models import QuerySet

from telegram_bot.models import User, ScheduledTask
from wireguard.exceptions import VPNServerError
from wireguard.services.vpn_server import VPNServerService
from wireguard.tasks import on_user_subscription_date_updated


@admin.action(description='Update tasks')
def update_tasks(modeladmin: 'UserAdmin', request, queryset: QuerySet[User]):
    for telegram_id in queryset.values_list('telegram_id', flat=True):
        on_user_subscription_date_updated.delay(telegram_id=telegram_id)
    modeladmin.message_user(request, 'Tasks updated')


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
        'subscription_expires_at',
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
    actions = (update_tasks,)

    @admin.display(boolean=True)
    def is_subscribed(self, obj):
        return obj.is_subscribed

    def save_model(self, request, obj: User, form, change):
        old_user: User = self.model.objects.filter(id=obj.id).select_related('server').first()
        is_server_changed = obj.server.is_changed(old_user.server)
        if is_server_changed:
            try:
                with VPNServerService(base_url=old_user.server.url,
                                      password=old_user.server.password) as old_vpn_server:
                    old_vpn_server.login()
                    old_vpn_server.delete_user(old_user.uuid)
            except VPNServerError:
                logging.error('Could not delete user from old server')
        with VPNServerService(base_url=obj.server.url, password=obj.server.password) as new_vpn_server:
            new_vpn_server.login()
            user_in_vpn_server, _ = new_vpn_server.get_or_create_user(obj.telegram_id)
            obj.uuid = user_in_vpn_server.uuid
            if obj.is_subscribed:
                new_vpn_server.enable_user(obj.uuid)
                if obj.subscribed_at != old_user.subscribed_at:
                    on_user_subscription_date_updated.delay(telegram_id=obj.telegram_id)
            else:
                new_vpn_server.disable_user(obj.uuid)
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
