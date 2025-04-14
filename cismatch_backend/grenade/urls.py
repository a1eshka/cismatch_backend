from django.urls import path


from . import api

urlpatterns = [
    path('', api.daily_grenade, name='daily_grenade'),
]
