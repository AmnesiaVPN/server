from django.urls import path

from wireguard.views import user_config_detail_api

urlpatterns = [
    path('<int:telegram_id>/config/', user_config_detail_api),
]
