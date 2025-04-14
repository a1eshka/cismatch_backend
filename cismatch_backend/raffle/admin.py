from django.contrib import admin

from .models import Raffle, Task, Ticket, Skin, UserTask

admin.site.register(Raffle)
admin.site.register(Ticket)
admin.site.register(Skin)
admin.site.register(Task)
admin.site.register(UserTask)