from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class SuperuserRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy('admin:login')

    def test_func(self):
        return self.request.user.is_superuser
