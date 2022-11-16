from django.urls import path
from donationalerts.views import payment_confirm_view

urlpatterns = [
    path('<str:telegram_id>/payment/', payment_confirm_view),
]
