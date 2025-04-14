from django.urls import path

from . import api

urlpatterns = [
    path('', api.advert_list, name='api_adverts_list'),
    path('mininews/', api.mininews_list, name='api_mininews_list'),

]