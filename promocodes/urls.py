from django.urls import path
from promocodes.views import PromocodeActivateApi

urlpatterns = [
    path('users/<int:telegram_id>/', PromocodeActivateApi.as_view()),
]
