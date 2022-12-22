from django.contrib import admin

from telegram_bot.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('registered_at',)
    search_fields = ('telegram_id',)
    search_help_text = 'User Telegram ID'
