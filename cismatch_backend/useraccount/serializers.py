from rest_framework import serializers

from .models import PromoCode, SkinBuyOrder, User

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'email',
            'steam_id',
            'trade_url',
            'avatar_url',
            'steam_avatar',
            'background_profile_url',
            'balance'
        )
        read_only_fields = ['id', 'steam_id', 'steam_avatar', 'balance']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'email',
            'steam_id',
            'trade_url',
            'avatar_url',
            'steam_avatar',
        )
        read_only_fields = ['id', 'steam_id', 'steam_avatar'] 

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['id', 'code', 'amount', 'is_used', 'user', 'created_at', 'expires_at']

class SkinBuyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinBuyOrder
        fields = '__all__'
        