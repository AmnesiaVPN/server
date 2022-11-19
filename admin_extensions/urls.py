from django.urls import path
from admin_extensions.views import BroadcastView

urlpatterns = [
    path('broadcast/', BroadcastView.as_view(), name='broadcast'),
]
