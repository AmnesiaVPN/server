import json
from typing import Generator, Iterable

import httpx
from pydantic import parse_obj_as

from donationalerts.schemas import Donation
from donationalerts.exceptions import DonationalertsError


class DonationAlertsAPIService:
    __slots__ = ('__access_token', '__attempts_on_server_error_count')

    def __init__(self, access_token: str, *, attempts_on_server_error_count: int = 10):
        self.__access_token = access_token
        self.__attempts_on_server_error_count = attempts_on_server_error_count

    @property
    def headers(self) -> dict:
        return {'Authorization': f'Bearer {self.__access_token}'}

    def iter_all_donations(self, *, page: int = 1) -> Generator[list[Donation], None, None]:
        url = 'https://www.donationalerts.com/api/v1/alerts/donations'
        server_errors_count = 0
        with httpx.Client(headers=self.headers) as client:
            while True:
                if server_errors_count >= self.__attempts_on_server_error_count:
                    raise DonationalertsError

                params = {'page': page}

                try:
                    response = client.get(url, params=params)
                except httpx.HTTPError:
                    server_errors_count += 1
                    continue

                if response.is_server_error:
                    server_errors_count += 1
                    continue

                try:
                    response_json = response.json()
                except json.JSONDecodeError:
                    raise DonationalertsError

                if not response_json['data']:
                    break
                yield parse_obj_as(list[Donation], response_json['data'])
                page += 1

                if response_json['links']['next'] is None:
                    break


def find_donations_with_specific_message(text: str, donations: Iterable[Donation]) -> list[Donation]:
    return [donation for donation in donations if text.lower() in donation.message.lower()]
