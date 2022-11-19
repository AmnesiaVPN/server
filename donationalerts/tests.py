import datetime
from typing import Generator

from django.test import SimpleTestCase

from donationalerts.exceptions import UserPaymentNotFoundError
from donationalerts.schemas import Donation
from donationalerts.services import is_donation_time_expired, find_donations_with_specific_message, find_user_donation


class TestDonationalerts(SimpleTestCase):

    def setUp(self) -> None:
        self.donations = [
            Donation(
                id=1,
                message='534654234',
                amount=1,
                currency='RUB',
                created_at=datetime.datetime.utcnow(),
            ),
            Donation(
                id=2,
                message='Hello world',
                amount=1,
                currency='RUB',
                created_at=datetime.datetime.utcnow(),
            ),
            Donation(
                id=3,
                message='      hello wOrld',
                amount=1,
                currency='RUB',
                created_at=datetime.datetime.utcnow(),
            ),
        ]

    def test_is_donation_time_not_expired(self):
        now = datetime.datetime.utcnow()
        donation_times = [
            now - datetime.timedelta(hours=23, minutes=59),
            now - datetime.timedelta(hours=2, minutes=0),
            now + datetime.timedelta(hours=54, minutes=59),
        ]
        for donation_time in donation_times:
            self.assertFalse(is_donation_time_expired(donation_time))

    def test_is_donation_time_expired(self):
        now = datetime.datetime.utcnow()
        donation_times = [
            now - datetime.timedelta(hours=24),
            now - datetime.timedelta(hours=53),
        ]
        for donation_time in donation_times:
            self.assertTrue(is_donation_time_expired(donation_time))

    def find_donations_and_get_ids(self, specific_message: str) -> set[int]:
        found_donations = find_donations_with_specific_message(specific_message, self.donations)
        return {donation.id for donation in found_donations}

    def test_find_donations_with_specific_message(self):
        self.assertSetEqual({2, 3}, self.find_donations_and_get_ids('hello world'))
        self.assertSetEqual({1}, self.find_donations_and_get_ids('534654234'))
        self.assertSetEqual(set(), self.find_donations_and_get_ids('spameggs'))
