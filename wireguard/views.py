from django.http import HttpResponse

from wireguard.tasks import get_user_config


def user_config_view(request, telegram_id: int):
    config_text = get_user_config(telegram_id)
    return HttpResponse(
        config_text,
        content_type='text/html; charset=utf-8',
    )
