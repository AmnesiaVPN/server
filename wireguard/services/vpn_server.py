import contextlib
import uuid

import httpx
from pydantic import parse_obj_as

from telegram_bot.exceptions import UserNotFoundError
from telegram_bot.models import User

from wireguard import exceptions
from wireguard.schemas import User, UserCreated


def handle_status_code(status_code: int):
    if 200 <= status_code <= 399:
        return
    elif status_code == 401:
        raise exceptions.UnauthorizedError
    raise exceptions.VPNServerError('Unexpected exception')


def login(client: httpx.Client, password: str) -> None:
    response = client.post('/api/session', json={'password': password})
    handle_status_code(response.status_code)


def logout(client: httpx.Client) -> None:
    response = client.delete('/api/session')
    handle_status_code(response.status_code)


def get_all_users(client: httpx.Client) -> list[User]:
    response = client.get('/api/wireguard/client')
    handle_status_code(response.status_code)
    return parse_obj_as(list[User], response.json())


def create_user(client: httpx.Client, name: str) -> UserCreated:
    response = client.post('/api/wireguard/client', json={'name': name})
    handle_status_code(response.status_code)
    return UserCreated.parse_obj(response.json())


def get_user_config_file(client: httpx.Client, user_uuid: uuid.UUID):
    response = client.get(f'/api/wireguard/client/{str(user_uuid)}/configuration')
    handle_status_code(response.status_code)
    return response


def delete_user(client: httpx.Client, user_uuid: uuid.UUID):
    response = client.delete(f'/api/wireguard/client/{str(user_uuid)}')
    handle_status_code(response.status_code)


def disable_user(client: httpx.Client, user_uuid: uuid.UUID):
    response = client.post(f'/api/wireguard/client/{str(user_uuid)}/disable')
    handle_status_code(response.status_code)


def enable_user(client: httpx.Client, user_uuid: uuid.UUID):
    response = client.post(f'/api/wireguard/client/{str(user_uuid)}/enable')
    handle_status_code(response.status_code)


@contextlib.contextmanager
def connected_client(base_url: str, password: str) -> httpx.Client:
    with httpx.Client(base_url=base_url) as client:
        login(client, password)
        yield client


def get_user_config(telegram_id: int) -> str:
    user = User.objects.select_related('server').filter(telegram_id=telegram_id).first()
    if not user:
        raise UserNotFoundError
    with vpn_server.connected_client(user.server.url, user.server.password) as client:
        return vpn_server.get_user_config_file(client, user.uuid).text.strip()
