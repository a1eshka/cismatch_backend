import requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .serializers import SkinBuyOrderSerializer
from .models import SkinBuyOrder, User
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SkinBuyOrder


@csrf_exempt
def link_steam(request):
    user = request.user
    
    # Получаем steam_id из сессии (после авторизации через Steam)
    steam_id = request.session.get('steam_id')
    if not steam_id:
        return JsonResponse({'success': False, 'error': 'Steam ID not found'})
    
    # Проверяем, не привязан ли уже Steam к другому аккаунту
    if User.objects.filter(steam_id=steam_id).exists():
        return JsonResponse({'success': False, 'error': 'Этот Steam-аккаунт уже привязан к другому пользователю'})
    
    # Получаем данные о пользователе из Steam API
    api_key = settings.STEAM_API_KEY
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        player_data = data['response']['players'][0]
        
        # Обновляем профиль пользователя
        user.steam_id = steam_id
        user.steam_avatar = player_data.get('avatarfull')
        user.save()
        
        return JsonResponse({'success': True, 'steam_avatar': user.steam_avatar})
    else:
        return JsonResponse({'success': False, 'error': 'Не удалось получить данные из Steam'})


