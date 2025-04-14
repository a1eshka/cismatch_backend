from django.urls import path


from . import api

urlpatterns = [
    path('', api.get_server, name='server_list'),
    #path('<int:server_id>/', api.ServerInfoView, name='server_info'),
    path('third-party/', api.get_third_party_servers, name='get_third_party_servers'),
    path('third-party/user/', api.get_user_servers, name='user-servers'),
    path('third-party/create/', api.create_third_party_server, name='create_third_party_server'),
    path('third-party/update/<uuid:server_id>/', api.update_third_party_server, name='update_third_party_server'),
    path('server-types/', api.get_server_types, name='get_server_types'),
    path('delete/<uuid:server_id>/', api.delete_server, name='delete_server'),   
]
