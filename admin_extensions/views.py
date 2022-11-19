from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from admin_extensions.forms import BroadcastForm


class BroadcastView(FormView):
    template_name = 'admin_extensions/broadcast.html'
    form_class = BroadcastForm
    success_url = reverse_lazy('broadcast')

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Рассылка создана')
        return super().form_valid(form)
