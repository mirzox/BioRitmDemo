from django.contrib import admin
from django.db.models import Q

from .models import Parameters, Services, Category
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    search_fields = ['name']
    fields = ["name", "items_count", "is_continuous"]
    readonly_fields = ["items_count"]
    list_display = ['name', 'items_count', 'is_continuous']
    # list_display_links = ['items_count']
    list_editable = ['is_continuous']

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        queryset = Category.objects.filter(Q(name__icontains=search_term.title()) |
                                           Q(name__icontains=search_term.lower()) |
                                           Q(name__contains=search_term.upper()))
        return queryset, False


class ServiceAdmin(admin.ModelAdmin):
    model = Category
    list_filter = ['category_id']
    search_fields = ['name__contains']
    list_display = ['category_id', 'name', 'price', 'fee']
    list_editable = ['name', 'price', 'fee']
    sortable_by = ['category_id', 'name', 'price', 'fee']
    list_per_page = 20

    def get_search_results(self, request, queryset, search_term):
        if queryset and not len(search_term):
            return queryset, False
        # search_term is what you input in admin site
        queryset = queryset.filter(Q(name__icontains=search_term.title()) |
                                   Q(name__icontains=search_term.lower()) |
                                   Q(name__contains=search_term.upper()))
        return queryset, False


class ParameterAdmin(admin.ModelAdmin):
    model = Parameters
    search_fields = ['name']
    fields = ["name", "norm"]
    list_display = ['name', 'norm']
    list_editable = ['norm']
    list_per_page = 20

    def get_search_results(self, request, queryset, search_term):
        # search_term is what you input in admin site
        queryset = Parameters.objects.filter(Q(name__icontains=search_term.title()) |
                                             Q(name__icontains=search_term.lower()) |
                                             Q(name__contains=search_term.upper()))
        return queryset, False


admin.site.register(Parameters, ParameterAdmin)
admin.site.register(Services, ServiceAdmin)
admin.site.register(Category, CategoryAdmin)
