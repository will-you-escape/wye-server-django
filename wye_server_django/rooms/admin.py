from django.contrib import admin

from rooms.models import EscapeRoomSession


class EscapeRoomSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(EscapeRoomSession, EscapeRoomSessionAdmin)
