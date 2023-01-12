import json
import re
from typing import Generator, Iterable

import httpx
from pydantic import parse_obj_as

from donationalerts.exceptions import DonationalertsError
from donationalerts.schemas import DonationalertsPayment, ValidatedDonationalertsPayment


class DonationAlertsAPIService:
    __slots__ = ('__access_token',)

    def __init__(self, access_token: str):
        self.__access_token = access_token

    @property
    def __authorization_headers(self) -> dict:
        return {'Authorization': f'Bearer {self.__access_token}'}

    def get_all_payments(self) -> list[DonationalertsPayment]:
        return [
            payment
            for payments_page in self.iter_all_payments()
            for payment in payments_page
        ]

    def iter_all_payments(self, *, page: int = 1) -> Generator[list[DonationalertsPayment], None, None]:
        url = 'https://www.donationalerts.com/api/v1/alerts/donations'
        with httpx.Client(headers=self.__authorization_headers) as client:
            while True:
                request_query_params = {'page': page}
                try:
                    response = client.get(url, params=request_query_params)
                except httpx.HTTPError:
                    raise DonationalertsError('HTTP request error')

                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    raise DonationalertsError('Could not decode response JSON')

                yield parse_obj_as(list[DonationalertsPayment], response_data['data'])
                page += 1
                if response_data['links']['next'] is None:
                    break


class DonationalertsPaymentSerializer:

    def __init__(
            self,
            *,
            payment: DonationalertsPayment,
            existing_telegram_ids: Iterable[int],
            previously_existing_payment_ids: Iterable[int],

    ):
        self.__payment = payment
        self.__existing_telegram_ids = existing_telegram_ids
        self.__previously_existing_payment_ids = previously_existing_payment_ids
        self.__validated_payment = None

    @property
    def validated_payment(self) -> ValidatedDonationalertsPayment | None:
        return self.__validated_payment

    @property
    def has_message(self) -> bool:
        return bool(self.__payment.message)

    @property
    def is_already_existed(self) -> bool:
        return self.__payment.id in self.__previously_existing_payment_ids

    def is_valid(self) -> bool:
        if not self.has_message:
            return False
        if self.is_already_existed:
            return False
        possible_telegram_ids = find_integer_numbers(self.__payment.message)
        for telegram_id in possible_telegram_ids:
            if telegram_id not in self.__existing_telegram_ids:
                continue
            self.__validated_payment = ValidatedDonationalertsPayment(**self.__payment.dict(), telegram_id=telegram_id)
            return True
        return False


def find_integer_numbers(text: str | None) -> list[int]:
    if text is None:
        return []
    pattern = re.compile(r'\d{8,}')
    found_integers: list[str] = re.findall(pattern, text)
    return [int(integer_number) for integer_number in found_integers]


def filter_valid_payments(
        *,
        payments: Iterable[DonationalertsPayment],
        existing_telegram_ids: Iterable[int],
        previously_existing_payment_ids: Iterable[int],
) -> list[ValidatedDonationalertsPayment]:
    return [
        payment_serializer.validated_payment
        for payment in payments
        if (payment_serializer := DonationalertsPaymentSerializer(
            payment=payment,
            existing_telegram_ids=existing_telegram_ids,
            previously_existing_payment_ids=previously_existing_payment_ids,
        )).is_valid()
    ]
