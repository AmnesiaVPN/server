from django.db.models import Count, F, QuerySet

from wireguard.exceptions import NoFreeServersError
from wireguard.models import Server

__all__ = (
    'get_blankest_server',
    'filter_servers_with_blank_slots',
    'get_servers_sorted_by_users_count',
)


def get_servers_sorted_by_users_count() -> QuerySet[Server]:
    return (
        Server.objects
        .annotate(users_count=Count('user__server'))
        .order_by('users_count', '-max_users_count')
    )


def filter_servers_with_blank_slots(servers: QuerySet[Server]) -> QuerySet[Server]:
    return servers.filter(users_count__lt=F('max_users_count'))


def get_blankest_server() -> Server:
    # TODO учитывать количество АКТИВНЫХ юзеров при сортировке, то есть юзеров с активной подпиской
    servers = get_servers_sorted_by_users_count()
    servers_with_blank_slots = filter_servers_with_blank_slots(servers)

    if servers_with_blank_slots.exists():
        return servers_with_blank_slots.first()

    server = servers.first()
    if not server:
        raise NoFreeServersError
    return server
