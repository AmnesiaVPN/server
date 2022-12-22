from django.contrib import admin

from donationalerts.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_filter = ('is_used',)
    list_display = ('donation_id', 'is_used', 'created_at')
    search_fields = ('user__telegram_id',)
    search_help_text = 'User Telegram ID'
