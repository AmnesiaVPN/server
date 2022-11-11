from django.urls import path

from telegram_bot.views import (
    get_user_view,
    create_user_view,
)

urlpatterns = [
    path('<int:telegram_id>/', get_user_view),
    path('', create_user_view),
]
