from .models import GrenadeThrow
from django.core.cache import cache
from datetime import date
from django.http import JsonResponse
import random

def get_daily_grenades(request):
    today = date.today().isoformat()

    flashes = list(GrenadeThrow.objects.filter(type="flash"))
    smokes = list(GrenadeThrow.objects.filter(type="smoke"))

    if not flashes or not smokes:
        return JsonResponse({"error": "Нет доступных гранат"}, status=404)

    random.seed(today)  # Генерируем один и тот же набор в день
    daily_flash = random.choice(flashes)  # 1 случайная флешка
    daily_smoke = random.choice(smokes)  # 1 случайный смок

    return JsonResponse({
        "flash": {"id": daily_flash.id, "name": daily_flash.name, "map_name": daily_flash.map_name, "description": daily_flash.description,  "video_webm_url": daily_flash.video_webm_url},
        "smoke": {"id": daily_smoke.id, "name": daily_smoke.name, "map_name": daily_smoke.map_name, "description": daily_smoke.description, "video_webm_url": daily_smoke.video_webm_url},
    })