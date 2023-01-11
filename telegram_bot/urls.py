from django.urls import path

from telegram_bot.views import (
    UserDetailApi,
    UserCreateApi,
)

urlpatterns = [
    path('<int:telegram_id>/', UserDetailApi.as_view()),
    path('', UserCreateApi.as_view()),
]
