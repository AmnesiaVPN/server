from django import forms
from django.utils.translation import gettext_lazy as _


class BroadcastForm(forms.Form):
    text = forms.CharField(
        max_length=4000,
        min_length=5,
        widget=forms.Textarea(attrs={'placeholder': '<b>Hello</b>'}),
        label=_('Broadcast message'),
    )
    results_notify_to = forms.IntegerField(
        required=False,
        label=_('Send report when finishes (chat ID)'),
        widget=forms.NumberInput(attrs={'placeholder': '283568193'}),
    )
