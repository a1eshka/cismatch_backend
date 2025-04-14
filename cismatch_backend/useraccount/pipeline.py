from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from django.utils.timezone import now

User = get_user_model()

def save_steam_data(backend, user, response, details, *args, **kwargs):
    if backend.name == 'steam':
        # Обновляем данные только если пользователь уже существует
        if not user.steam_id:
            user.steam_id = details['player']['steamid']
        user.name = details['player']['personaname']
        user.steam_avatar = details['player']['avatarfull']
        
        # Устанавливаем временную почту, если она отсутствует
        if not user.email:
            user.email = f"{uuid.uuid4()}@cismatch.ru"

        user.save()

        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Редирект на Next.js
        nextjs_url = f"http://localhost:3000/auth/callback?token={access_token}&refresh_token={refresh_token}&user_id={user.id}"
        return redirect(nextjs_url)
    

def associate_existing_steam_user(backend, uid, user=None, *args, **kwargs):
    """
    Проверяет, существует ли пользователь с таким Steam ID.
    Если существует — возвращает пользователя.
    """
    if backend.name == 'steam':
        try:
            # Проверяем, существует ли пользователь с данным Steam ID
            existing_user = User.objects.get(steam_id=uid)
            existing_user.last_login = now()
            existing_user.save()
            return {'user': existing_user}
        except User.DoesNotExist:
            # Пользователь с таким Steam ID не найден, продолжаем процесс создания
            pass
    return None
