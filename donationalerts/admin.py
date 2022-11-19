from django.contrib import admin

from donationalerts.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
