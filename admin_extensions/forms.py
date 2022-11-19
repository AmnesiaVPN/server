from django import forms
from django.utils.translation import gettext_lazy as _


class BroadcastForm(forms.Form):
    text = forms.CharField(max_length=4000, min_length=5, widget=forms.Textarea(), label=_('Broadcast message'))
    results_notify_to = forms.IntegerField(required=False)
