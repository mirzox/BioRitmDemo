from django.contrib import admin

from .models import Order, PId, ParamResult, Result
# Register your models here.
admin.site.register(Order)
admin.site.register(PId)
admin.site.register(ParamResult)
admin.site.register(Result)
