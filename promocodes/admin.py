from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ExportActionMixin

from promocodes.forms import PromocodesGroupCreateForm
from promocodes.models import PromocodesGroup, Promocode
from promocodes.services import batch_create_promocodes


class PromocodeResource(resources.ModelResource):
    class Meta:
        model = Promocode
        fields = ('group__name', 'value', 'activated_by__telegram_id', 'activated_at')


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
class PromocodeAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_classes = (PromocodeResource,)
    list_filter = ('group', PromocodeActivatedFilter)
    search_fields = ('value',)
    search_help_text = 'Promocode'
    list_display = ('value', 'group', 'activated_at',)


class PromocodeInline(admin.TabularInline):
    model = Promocode
    extra = False
    show_change_link = True
    readonly_fields = ('value', 'activated_by', 'activated_at')
    can_delete = False
    classes = ('collapse',)


@admin.register(PromocodesGroup)
class PromocodeGroupAdmin(admin.ModelAdmin):
    inlines = [PromocodeInline]
    list_display = ('name', 'total_activated', 'expire_at', 'total_count')
    form = PromocodesGroupCreateForm

    @admin.display()
    def total_activated(self, obj):
        return str(obj.promocode_set.exclude(activated_at=None).count())

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['total_activated']
        if obj is not None:
            readonly_fields.append('total_count')
        return super().get_readonly_fields(request, obj) + tuple(readonly_fields)

    def save_model(self, request, obj, form, change):
        init_promocodes = not obj.pk
        super().save_model(request, obj, form, change)
        if init_promocodes:
            count = form.cleaned_data['total_count']
            batch_create_promocodes(group=obj, count=count)
