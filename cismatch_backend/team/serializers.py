from rest_framework import serializers

from .models import Team
from useraccount.serializers import UserDetailSerializer

class TeamListSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True, many=False)
    teammates = UserDetailSerializer(read_only=True,many=True)
    class Meta:
        model = Team
        fields = (
            'id',
            'title',
            'body',
            'logo_url',
            'social_url',
            'teammates',
            'author'
        )

