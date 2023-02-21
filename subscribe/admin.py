from django.contrib import admin
from .models import Subscribe


# Register your models here.
class SubscribeAdmin(admin.ModelAdmin):
    search_fields = ('notice',)
    list_display = ('user', 'notice', 'notice_link', 'is_active')


admin.register(Subscribe, SubscribeAdmin)
