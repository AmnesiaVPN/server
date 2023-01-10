from django.contrib import admin
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from promocodes.models import PromocodesGroup, Promocode


class PromocodeActivatedFilter(admin.SimpleListFilter):
    title = _('promocode was activated')
    parameter_name = 'promocode_activated'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Only activated')),
            ('no', _('Only non-activated')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(activated_at=None)
        elif self.value() == 'no':
            return queryset.filter(activated_at=None)
        return queryset


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_filter = ('group', PromocodeActivatedFilter)
    search_fields = ('value',)
    search_help_text = 'Promocode'
    list_display = ('value', 'group', 'activated_at',)

    def has_add_permission(self, request):
        return False


class PromocodeInline(admin.TabularInline):
    model = Promocode
    extra = False


@admin.register(PromocodesGroup)
class PromocodeGroupAdmin(admin.ModelAdmin):
    inlines = [PromocodeInline]
    readonly_fields = ('total_activated',)
    list_display = ('name', 'total_activated', 'count', 'expire_at')

    @admin.display()
    def total_activated(self, obj):
        return str(obj.promocode_set.exclude(activated_at=None).count())

    def save_model(self, request, obj, form, change):
        promocodes = [Promocode(group=obj, value=get_random_string(length=8)) for _ in range(obj.count)]
        super().save_model(request, obj, form, change)
        Promocode.objects.bulk_create(promocodes, ignore_conflicts=True)
