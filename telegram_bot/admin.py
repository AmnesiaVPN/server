import logging

import httpx
from django.contrib import admin, messages
from django.db.models import QuerySet
from rest_framework.request import Request

from telegram_bot.models import User
from wireguard.exceptions import VPNServerError
from wireguard.models import Server
from wireguard.services.vpn_server import VPNServerService


def on_user_server_changed(*, request: Request, user: User, server: Server) -> None:
    try:
        with VPNServerService(base_url=server.url, password=server.password) as vpn_server:
            vpn_server.login()
            vpn_server.delete_user(user.uuid)
    except (VPNServerError, httpx.HTTPError):
        error_text = 'Could not delete user from old server'
        messages.error(request, error_text)
        logging.error(error_text)


def update_user_in_server(*, request: Request, user: User, server: Server) -> None:
    try:
        with VPNServerService(base_url=server.url, password=server.password) as new_vpn_server:
            new_vpn_server.login()
            user_in_vpn_server, _ = new_vpn_server.get_or_create_user(user.telegram_id)
            user.uuid = user_in_vpn_server.uuid
            if user.is_subscribed:
                new_vpn_server.enable_user(user.uuid)
                check_user_enabled_and_add_messages(request, new_vpn_server, user.telegram_id)
            else:
                new_vpn_server.disable_user(user.uuid)
                check_user_disabled_and_add_messages(request, new_vpn_server, user.telegram_id)
    except (VPNServerError, httpx.HTTPError):
        messages.error(request, 'Could not connect to the server')


def check_user_enabled_and_add_messages(request: Request, vpn_server: VPNServerService, telegram_id: int):
    enabled_message_text = 'User has been enabled in the Wireguard Server'
    not_enabled_message_text = 'User has not been enabled in the Wireguard Server'
    try:
        is_user_enabled = vpn_server.is_user_enabled(telegram_id)
    except VPNServerError:
        messages.error(request, not_enabled_message_text)
    else:
        if is_user_enabled:
            messages.info(request, enabled_message_text)
        else:
            messages.error(request, not_enabled_message_text)


def check_user_disabled_and_add_messages(request: Request, vpn_server: VPNServerService, telegram_id: int):
    disabled_message_text = 'User has been disabled in the Wireguard Server'
    not_disabled_message_text = 'User has not been disabled in the Wireguard Server'
    try:
        is_user_disabled = vpn_server.is_user_disabled(telegram_id)
    except VPNServerError:
        messages.error(request, not_disabled_message_text)
    else:
        if is_user_disabled:
            messages.info(request, disabled_message_text)
        else:
            messages.error(request, not_disabled_message_text)


@admin.action(description='Update tasks')
def update_tasks(modeladmin: 'UserAdmin', request, queryset: QuerySet[User]):
    modeladmin.message_user(request, 'Tasks updated')


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
            on_user_server_changed(request=request, user=old_user, server=old_user.server)
        update_user_in_server(request=request, user=obj, server=obj.server)
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
