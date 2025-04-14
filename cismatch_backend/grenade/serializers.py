from rest_framework import serializers
from .models import GrenadeThrow

class GrenadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrenadeThrow
        fields = "__all__"
