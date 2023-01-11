import logging
from uuid import UUID

import httpx
from pydantic import parse_obj_as

from telegram_bot.models import User
from wireguard.exceptions import VPNServerError, UnauthorizedError
from wireguard.schemas import User, UserCreated

__all__ = ('VPNServerService',)


class VPNServerService:

    def __init__(self, *, base_url: str, password: str):
        self.__base_url = base_url
        self.__password = password
        self.__client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.logout()
        except VPNServerError:
            logging.warning('Could not logout')
        try:
            self.client.close()
        except UnauthorizedError:
            logging.warning('Client did not log in, no need to close')

    @property
    def client(self) -> httpx.Client:
        if self.__client is None:
            raise UnauthorizedError('Call "login()" before using other methods')
        return self.__client

    @client.setter
    def client(self, client: httpx.Client) -> None:
        self.__client = client

    def login(self) -> None:
        url = '/api/session'
        request_body = {'password': self.__password}
        client = httpx.Client(base_url=self.__base_url)
        response = client.post(url, json=request_body)
        if response.status_code != 204:
            raise VPNServerError
        self.client = client

    def logout(self) -> None:
        url = '/api/session'
        response = self.client.delete(url)
        if response.status_code != 204:
            raise VPNServerError

    def get_all_users(self) -> tuple[User, ...]:
        url = '/api/wireguard/client'
        response = self.client.get(url)
        response_data = response.json()
        return parse_obj_as(tuple[User, ...], response_data)

    def create_user(self, telegram_id: int | str) -> UserCreated:
        url = '/api/wireguard/client'
        request_data = {'name': str(telegram_id)}
        response = self.client.post(url, json=request_data)
        response_data = response.json()
        return UserCreated.parse_obj(response_data)

    def get_user_config_file(self, user_uuid: str | UUID) -> str:
        url = f'/api/wireguard/client/{str(user_uuid)}/configuration'
        response = self.client.get(url)
        return response.text

    def delete_user(self, user_uuid: str | UUID):
        url = f'/api/wireguard/client/{str(user_uuid)}'
        response = self.client.delete(url)
        if response.status_code != 204:
            raise VPNServerError

    def disable_user(self, user_uuid: str | UUID):
        url = f'/api/wireguard/client/{str(user_uuid)}/disable'
        response = self.client.post(url)
        if response.status_code != 204:
            raise VPNServerError

    def enable_user(self, user_uuid: str | UUID):
        url = f'/api/wireguard/client/{str(user_uuid)}/enable'
        response = self.client.post(url)
        if response.status_code != 204:
            raise VPNServerError

    def get_user(self, telegram_id: int | str) -> User:
        users = self.get_all_users()
        users = [user for user in users if user.name == str(telegram_id)]
        if not users:
            raise VPNServerError
        return users[0]

    def get_or_create_user(self, telegram_id: int | str) -> tuple[User, bool]:
        try:
            return self.get_user(telegram_id), False
        except VPNServerError:
            self.create_user(telegram_id)
            return self.get_user(telegram_id), True
