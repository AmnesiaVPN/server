from django.contrib import admin
from django.urls import path, include

from wireguard.views import UserConfigDetailApi
from telegram_bot.views import UserCreateApi, UserDetailApi
from promocodes.views import PromocodeActivateApi

api_patterns = [
    path('users/', include([
        path('', UserCreateApi.as_view()),
        path('<int:telegram_id>/', UserDetailApi.as_view()),
        path('<int:telegram_id>/promocodes/', PromocodeActivateApi.as_view()),
        path('<int:telegram_id>/config/', UserConfigDetailApi.as_view()),
    ]))
]

urlpatterns = [
    path('admin/', include('admin_extensions.urls')),
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns))
]
