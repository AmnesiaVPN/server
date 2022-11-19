import datetime
from typing import Generator, Iterable

import httpx
from pydantic import parse_obj_as

from donationalerts.schemas import Donation


class DonationAlertsClient:
    __slots__ = ('__access_token',)

    def __init__(self, access_token: str):
        self.__access_token = access_token

    @property
    def headers(self) -> dict:
        return {'Authorization': f'Bearer {self.__access_token}'}

    def iter_all_donations(self, *, page: int = 1) -> Generator[list[Donation], None, None]:
        url = 'https://www.donationalerts.com/api/v1/alerts/donations'
        with httpx.Client(headers=self.headers) as client:
            while True:
                params = {'page': page}
                response = client.get(url, params=params)
                response_json = response.json()
                if not response_json['data']:
                    break
                yield parse_obj_as(list[Donation], response_json['data'])
                if response_json['links']['next'] is None:
                    break
                page += 1


def find_donations_with_specific_message(text: str, donations: Iterable[Donation]) -> list[Donation]:
    return [donation for donation in donations if text.lower() in donation.message.lower()]


def is_donation_time_expired(donation_time: datetime.datetime) -> bool:
    delta = datetime.datetime.utcnow() - donation_time
    day_in_seconds = 24 * 60 * 60
    return delta.total_seconds() > day_in_seconds
