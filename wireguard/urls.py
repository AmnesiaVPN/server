from django.urls import path

from wireguard.views import user_config_view

urlpatterns = [
    path('<int:telegram_id>/config/', user_config_view),
]
