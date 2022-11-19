from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from admin_extensions.forms import BroadcastForm
from admin_extensions.mixins import SuperuserRequiredMixin
from telegram_bot.tasks import start_broadcasting


class BroadcastView(SuperuserRequiredMixin, FormView):
    template_name = 'admin_extensions/broadcast.html'
    form_class = BroadcastForm
    success_url = reverse_lazy('broadcast')

    def form_valid(self, form):
        text = form.cleaned_data['text']
        results_notify_to = form.cleaned_data['results_notify_to']
        start_broadcasting.delay(text, results_notify_to)
        messages.add_message(self.request, messages.SUCCESS, 'Рассылка создана')
        return super().form_valid(form)
