from django.contrib import admin

from .models import Server, ServerType, ThirdPartyServer

admin.site.register(Server)
admin.site.register(ServerType)
admin.site.register(ThirdPartyServer)


