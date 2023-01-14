from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from telegram_bot.selectors import get_user
from telegram_bot.services.users import create_user
from wireguard.selectors import get_blankest_server
from wireguard.services.vpn_server import VPNServerService
from wireguard.tasks import on_user_subscription_date_updated


class UserOutputMixin:
    class OutputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()
        is_trial_period = serializers.BooleanField()
        subscribed_at = serializers.DateTimeField()
        subscription_expires_at = serializers.DateTimeField()
        is_subscribed = serializers.BooleanField()
        has_activated_promocode = serializers.BooleanField()


class UserDetailApi(APIView, UserOutputMixin):

    def get(self, request, telegram_id: int):
        user = get_user(telegram_id=telegram_id)
        serializer = self.OutputSerializer(user)
        return Response(serializer.data)


class UserCreateApi(APIView, UserOutputMixin):
    class InputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telegram_id: int = serializer.data['telegram_id']

        server = get_blankest_server()
        with VPNServerService(base_url=server.url, password=server.password) as vpn_server:
            vpn_server.login()
            user_in_vpn_server, is_created = vpn_server.get_or_create_user(telegram_id)

        user = create_user(telegram_id=telegram_id, user_uuid=user_in_vpn_server.uuid, server=server)
        on_user_subscription_date_updated.delay(telegram_id=user.telegram_id)

        serializer = self.OutputSerializer(user)
        return Response(serializer.data)
