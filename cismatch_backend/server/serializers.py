from rest_framework import serializers
from .models import ThirdPartyServer, ServerType
from useraccount.serializers import UserDetailSerializer

class ServerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerType
        fields = ['id', 'title']

class ThirdPartyServerSerializer(serializers.ModelSerializer):
    server_type = ServerTypeSerializer()
    owner = UserDetailSerializer(read_only=True, many=False)
    class Meta:
        model = ThirdPartyServer
        fields = [
            'id', 'ip', 'port', 'server_type', 'owner', 'description',
            'is_paid', 'is_boosted', 'published', 'boost_expires_at', 'createdAt', 'updateAt'
        ]
        read_only_fields = ['createdAt', 'updateAt']
