from django.contrib import admin

from account.models import WYEUser


class WYEUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(WYEUser, WYEUserAdmin)
