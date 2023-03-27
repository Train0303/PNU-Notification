from django.contrib import admin

from .models import Notice, HakjisiNotice


# Register your models here.
class NoticeAdmin(admin.ModelAdmin):
    search_fields = ('rss_link', )
    list_display = ('rss_link', 'updated_at')


class HakjisiNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice_link', 'last_notice_id')


admin.site.register(Notice, NoticeAdmin)
admin.site.register(HakjisiNotice, HakjisiNoticeAdmin)