from django.urls import path
from promocodes.views import activate_promocode_view

urlpatterns = [
    path('users/<int:telegram_id>/', activate_promocode_view),
]
