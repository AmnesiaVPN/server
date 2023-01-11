from django.http import HttpResponse

from telegram_bot.selectors import get_user_or_raise_404
from wireguard.services.vpn_server import VPNServerService


def user_config_detail_api(request, telegram_id: int):
    user = get_user_or_raise_404(telegram_id=telegram_id, include_server=True)
    with VPNServerService(base_url=user.server.url, password=user.server.password) as vpn_server:
        vpn_server.login()
        config_text = vpn_server.get_user_config_file(user.uuid)
    return HttpResponse(config_text, content_type='text/html; charset=utf-8')
