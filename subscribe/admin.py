from django.contrib import admin
from .models import Subscribe, HakjisiSubscribe


# Register your models here.
class SubscribeAdmin(admin.ModelAdmin):
    search_fields = ('notice',)
    list_display = ('user', 'notice', 'notice_link', 'is_active')


class HakjisiSubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'notice', 'is_active')


admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(HakjisiSubscribe, HakjisiSubscribeAdmin)