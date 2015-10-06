from django.contrib import admin

from .models import Config, Person, Device, Log

admin.site.register(Person)

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enabled')
    list_per_page = 30
    list_filter = ('config_type',)

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created')
    list_per_page = 30
    list_filter = ('log_type', 'status', 'device')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_home')

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['ip'].initial = request.META['REMOTE_ADDR']
        return form
