from django.contrib import admin
from django.contrib.auth.models import User

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Photo, ChoiceCategories
# Register your models here.


class CategoryChoicesAdmin(admin.ModelAdmin):
    model = ChoiceCategories
    # search_fields = ['user_id__first_name']
    list_display = ['user_id']


admin.site.register(ChoiceCategories, CategoryChoicesAdmin)
admin.site.register(Photo)
admin.site.unregister(User)


class UserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def get_readonly_fields(self, request, obj=None):
        rof = super(UserAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            rof += ('is_staff', 'is_superuser', 'user_permissions')
        return rof


admin.site.register(User, UserAdmin)
