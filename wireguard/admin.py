from django.contrib import admin

from wireguard.models import Server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    pass
