from .views import get_daily_grenades
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import GrenadeThrow
from .serializers import GrenadeSerializer
from django.http import JsonResponse
from datetime import date
import random

class GrenadeViewSet(viewsets.ModelViewSet):
    queryset = GrenadeThrow.objects.all()
    serializer_class = GrenadeSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def daily_grenade(request):
    today = date.today().isoformat()

    flashes = list(GrenadeThrow.objects.filter(grenade_type="flash"))
    smokes = list(GrenadeThrow.objects.filter(grenade_type="smoke"))

    if not flashes or not smokes:
        return JsonResponse({"error": "Нет доступных гранат"}, status=404)

    random.seed(today)  # Генерируем один и тот же набор в день
    daily_flash = random.choice(flashes)  # 1 случайная флешка
    daily_smoke = random.choice(smokes)  # 1 случайный смок

    return JsonResponse({
        "flash": {"id": daily_flash.id, "name": daily_flash.name, "map_name": daily_flash.map_name, "description": daily_flash.description,  "video_webm_url": daily_flash.video_webm_url},
        "smoke": {"id": daily_smoke.id, "name": daily_smoke.name, "map_name": daily_smoke.map_name, "description": daily_smoke.description, "video_webm_url": daily_smoke.video_webm_url},
    })
