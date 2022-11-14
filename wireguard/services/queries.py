from django.db.models import F, Count

from wireguard.models import Server


def get_server_with_fewer_users() -> Server:
    server = (
        Server.objects
        .annotate(users_count=Count('user__server'))
        .filter(users_count__lt=F('max_users_count'))
        .order_by('users_count')).first()
    if not server:
        raise Server.DoesNotExist('No free servers')
    return server
