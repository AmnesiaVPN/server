from telegram_bot.models import User
from wireguard.services import vpn_server
from telegram_bot.exceptions import UserNotFoundError


def get_user_config(telegram_id: int) -> str:
    user = User.objects.select_related('server').filter(telegram_id=telegram_id).first()
    if not user:
        raise UserNotFoundError
    with vpn_server.connected_client(user.server.url, user.server.password) as client:
        return vpn_server.get_user_config_file(client, user.uuid).text.strip()
