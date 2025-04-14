from rest_framework import serializers

from .models import Advert, MiniNews
from useraccount.serializers import UserDetailSerializer

class AdvertListSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True, many=False)
    class Meta:
        model = Advert
        fields = (
            'id',
            'title',
            'body',
            'url',
            'advert_image_url',
            'published',
            'author'
        )

class MiniNewsListSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True, many=False)
    class Meta:
        model = MiniNews
        fields = (
            'id',
            'title',
            'url',
            'published',
            'author'
        )