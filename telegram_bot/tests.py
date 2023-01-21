import datetime
import uuid

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from telegram_bot.models import User
from wireguard.models import Server
from telegram_bot.selectors import get_subscription_expired_users


class SubscriptionExpiredUsersSelectorTestCase(TestCase):

    def setUp(self) -> None:
        now = timezone.now()
        server = Server.objects.create(url='http://localhost:5000', password='1234', max_users_count=100)
        User.objects.create(
            telegram_id=1, uuid=uuid.uuid4(), server=server, is_trial_period=False,
            subscribed_at=now - datetime.timedelta(days=settings.SUBSCRIPTION_DAYS, minutes=1),
        )
        User.objects.create(
            telegram_id=2, uuid=uuid.uuid4(), server=server, is_trial_period=False,
            subscribed_at=now - datetime.timedelta(days=settings.SUBSCRIPTION_DAYS, minutes=-1),
        )
        User.objects.create(
            telegram_id=3, uuid=uuid.uuid4(), server=server, is_trial_period=True,
            subscribed_at=now - datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS, minutes=1),
        )
        User.objects.create(
            telegram_id=4, uuid=uuid.uuid4(), server=server, is_trial_period=True,
            subscribed_at=now - datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS, minutes=-1),
        )
        User.objects.create(
            telegram_id=5, uuid=uuid.uuid4(), server=server, is_trial_period=True,
            subscribed_at=now - datetime.timedelta(days=settings.TRIAL_PERIOD_DAYS, hours=16),
        )
        User.objects.create(
            telegram_id=6, uuid=uuid.uuid4(), server=server, is_trial_period=False,
            subscribed_at=now - datetime.timedelta(days=settings.SUBSCRIPTION_DAYS, hours=-20),
        )
        self.expired_ids = {1, 3, 5}
        self.not_expired_ids = {2, 4, 6}

    def test_get_users_with_expired_subscription(self):
        users = get_subscription_expired_users().values_list('telegram_id', flat=True)
        for expired_id in self.expired_ids:
            self.assertIn(expired_id, users)

    def test_get_users_without_expired_subscription(self):
        users = get_subscription_expired_users().values_list('telegram_id', flat=True)
        for expired_id in self.not_expired_ids:
            self.assertNotIn(expired_id, users)
