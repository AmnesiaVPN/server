from django.contrib import admin

from telegram_bot.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('telegram_id', 'registered_at', 'subscribed_at')
