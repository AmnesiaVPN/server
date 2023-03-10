from django.http import HttpResponse
from rest_framework.views import APIView

from telegram_bot.selectors import get_user
from wireguard.services.vpn_server import VPNServerService


class UserConfigDetailApi(APIView):
    def get(self, request, telegram_id: int):
        user = get_user(telegram_id=telegram_id, include_server=True)
        with VPNServerService(base_url=user.server.url, password=user.server.password) as vpn_server:
            vpn_server.login()
            config_text = vpn_server.get_user_config_file(user.uuid)
        return HttpResponse(config_text, content_type='text/html; charset=utf-8')
