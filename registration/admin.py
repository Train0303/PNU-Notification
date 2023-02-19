from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('email',)
    list_display = ('id', 'email', 'date_joined')


admin.site.register(CustomUser, CustomUserAdmin)