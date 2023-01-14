from django import forms

from promocodes.models import PromocodesGroup

__all__ = ('PromocodesGroupCreateForm',)


class PromocodesGroupCreateForm(forms.ModelForm):
    total_count = forms.IntegerField(min_value=1, max_value=1000)

    class Meta:
        model = PromocodesGroup
        fields = '__all__'
