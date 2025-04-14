from django.urls import path

from . import api

urlpatterns = [
    path('', api.teams_list, name='api_teams_list'),
    path('create/', api.create_team, name='api_create_team'),
    path('join/<uuid:team_id>', api.join_team, name='api_join_team'),
    path('<uuid:pk>', api.team_detail, name='api_team_detail'),
]