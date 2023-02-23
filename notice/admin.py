from django.contrib import admin

from .models import Notice


# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
    search_fields = ('rss_link', )
    list_display = ('rss_link', 'updated_at')


admin.site.register(Notice, NoticeAdmin)
