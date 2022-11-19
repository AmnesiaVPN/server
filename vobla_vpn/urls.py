from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('admin_extensions.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('telegram_bot.urls')),
    path('users/', include('wireguard.urls')),
    path('users/', include('donationalerts.urls')),
]
