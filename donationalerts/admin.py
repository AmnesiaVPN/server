from django.contrib import admin

from donationalerts.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_filter = ('is_used',)
    list_display = ('donation_id', 'is_used',)
    readonly_fields = ('donation_id', 'created_at',)
