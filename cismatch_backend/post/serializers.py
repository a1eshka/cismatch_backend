from rest_framework import serializers

from .models import Post, Role, Status, TypePost, Comment
from useraccount.serializers import UserDetailSerializer, UserSerializer


class StatusDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = (
            'id',
            'title',
        )
class TypePostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePost
        fields = (
            'id',
            'title',
        )        

class RoleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            'id',
            'title',
        )  

class PostsListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    status = StatusDetailSerializer(read_only=True, many=False)
    type = TypePostDetailSerializer(read_only=True, many=False)
    role = RoleDetailSerializer(read_only=True, many=False)
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'body',
            'type',
            'status',
            'role',
            'author',
            'views',
            'createdAt',
            'published',
            'image_url',
            'formatted_date',
            'formatted_time',
        )
    def get_formatted_date(self, obj):
        # Преобразование даты в нужный формат
        return obj.createdAt.strftime('%d.%m.%Y')
    def get_formatted_time(self, obj):
        # Преобразование даты в нужный формат
        return obj.createdAt.strftime('%H:%M')

class PostsDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    status = StatusDetailSerializer(read_only=True, many=False)
    type = TypePostDetailSerializer(read_only=True, many=False)
    role = RoleDetailSerializer(read_only=True, many=False)
    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'body',
            'type',
            'status',
            'role',
            'published',
            'author',
            'views',
            'createdAt',
            'image_url',
        )
        
class TypePostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePost
        fields = (
            'id',
            'title',
        )   
class StatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = (
            'id',
            'title',
        )        

class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            'id',
            'title',
        )        


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'text', 'created_at','formatted_date','formatted_time')

    def get_formatted_date(self, obj):
        # Преобразование даты в нужный формат
        return obj.created_at.strftime('%d.%m.%Y')
    def get_formatted_time(self, obj):
        # Преобразование даты в нужный формат
        return obj.created_at.strftime('%H:%M')