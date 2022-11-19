import datetime

from django.test import SimpleTestCase

from donationalerts.schemas import Donation
from donationalerts.services import find_donations_with_specific_message


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

    def find_donations_and_get_ids(self, specific_message: str) -> set[int]:
        found_donations = find_donations_with_specific_message(specific_message, self.donations)
        return {donation.id for donation in found_donations}

    def test_find_donations_with_specific_message(self):
        self.assertSetEqual({2, 3}, self.find_donations_and_get_ids('hello world'))
        self.assertSetEqual({1}, self.find_donations_and_get_ids('534654234'))
        self.assertSetEqual(set(), self.find_donations_and_get_ids('spameggs'))
