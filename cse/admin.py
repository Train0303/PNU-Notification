from django.contrib import admin
from .models import CseNotice


# Register your models here.
class CseNoticeAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('id', 'title', 'link', 'pub_date', 'author')


admin.site.register(CseNotice, CseNoticeAdmin)
