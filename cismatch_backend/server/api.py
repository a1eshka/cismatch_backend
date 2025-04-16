import json
from django.conf import settings
from .froms import ThirdPartyServerForm
from .serializers import ThirdPartyServerSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework import status
from .models import Server, ServerType, ThirdPartyServer
import a2s
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404


User = get_user_model()

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_server(request):
        servers = Server.objects.all()
        server_data = []

        for server in servers:
            try:
                server_info = (server.ip, server.port)
                info = a2s.info(server_info)
                player_count = info.player_count
                max_players = info.max_players
                map_image_url = f"{settings.WEBSITE_URL}/media/servers/maps/{info.map_name}.webp"
                map_icon_url = f"{settings.WEBSITE_URL}/media/servers/icons/{info.map_name}.png"
                server_data.append({
                    'id': str(server.id),
                    'ip': server.ip,
                    'port': server.port,
                    'published': server.published,
                    'name': info.server_name,
                    'map': info.map_name,
                    'ping': info.ping,
                    'current_players': player_count,
                    'max_players': max_players,
                    'map_image': map_image_url,
                    'map_icon': map_icon_url
                })

            except Exception as e:
                # Обработка ошибок, например, если сервер недоступен
                server_data.append({
                    'id': str(server.id),
                    'ip': server.ip,
                    'port': server.port,
                    'error': str(e)
                })

        return JsonResponse({'data': server_data}, safe=False, status=200)



@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_third_party_servers(request):
    servers = ThirdPartyServer.objects.all()
    server_data = []

    for server in servers:
        try:
            server_info = (server.ip, server.port)
            info = a2s.info(server_info)
            player_count = info.player_count
            max_players = info.max_players
            map_image_url = f"{settings.WEBSITE_URL}/media/servers/maps/{info.map_name}.webp"
            map_icon_url = f"{settings.WEBSITE_URL}/media/servers/icons/{info.map_name}.png"

            # Сериализуем сервер
            serializer = ThirdPartyServerSerializer(server)
            server_info = serializer.data

            # Добавляем дополнительные поля
            server_info.update({
                'name': info.server_name,
                'map': info.map_name,
                'ping': info.ping,
                'current_players': player_count,
                'max_players': max_players,
                'map_image': map_image_url,
                'map_icon': map_icon_url,
            })

            server_data.append(server_info)
        except Exception as e:
            # Обработка ошибок, например, если сервер недоступен
            server_data.append({
                'id': str(server.id),
                'ip': server.ip,
                'port': server.port,
                'error': str(e)
            })

    return JsonResponse({'data': server_data}, safe=False, status=200)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_user_servers(request):
    user_id = request.GET.get('user_id')  # Получаем ID пользователя из запроса

    if not user_id:
        return JsonResponse({'error': 'user_id параметр обязателен'}, status=400)

    servers = ThirdPartyServer.objects.filter(owner_id=user_id)  # Фильтруем сервера пользователя
    server_data = []

    for server in servers:
        try:
            server_info = (server.ip, server.port)
            info = a2s.info(server_info)  # Получаем информацию о сервере через a2s
            player_count = info.player_count
            max_players = info.max_players
            map_image_url = f"{settings.WEBSITE_URL}/media/servers/maps/{info.map_name}.webp"
            map_icon_url = f"{settings.WEBSITE_URL}/media/servers/icons/{info.map_name}.png"
            

            # Сериализуем сервер
            serializer = ThirdPartyServerSerializer(server)
            server_info = serializer.data

            # Добавляем дополнительные данные
            server_info.update({
                'name': info.server_name,
                'map': info.map_name,
                'ping': info.ping,
                'current_players': player_count,
                'max_players': max_players,
                'map_image': map_image_url,
                'map_icon': map_icon_url,
            })

            server_data.append(server_info)
        except Exception as e:
            # Обработка ошибок, если сервер недоступен
            server_data.append({
                'id': str(server.id),
                'ip': server.ip,
                'port': server.port,
                'error': str(e)
            })

    return JsonResponse({'data': server_data}, safe=False, status=200)

@api_view(['POST'])
@permission_classes([])  # Здесь можно настроить разрешения, если нужно
@parser_classes([MultiPartParser, FormParser])  # Разрешаем обработку multipart/form-data
def create_third_party_server(request):
    """
    Обработчик для добавления стороннего сервера
    """
    form = ThirdPartyServerForm(request.data)  # request.data будет содержать как текстовые данные, так и файлы

    if form.is_valid():
        third_party_server = form.save(commit=False)
        third_party_server.owner = request.user  # Устанавливаем владельца
        third_party_server.save()

        return JsonResponse({'success': True, 'data': third_party_server.id}, status=201)

    return JsonResponse({'errors': form.errors}, status=400)

    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_server_types(request):
    server_types = ServerType.objects.all().values('id', 'title')  # Получаем id и name типов серверов
    return JsonResponse(list(server_types), safe=False)

@api_view(['DELETE'])
def delete_server(request, server_id):
    """
    API для удаления сервера из базы данных.
    Удаляет сервер только если текущий пользователь является его владельцем.
    """
    server = get_object_or_404(ThirdPartyServer, id=server_id)

    # Проверяем, является ли текущий пользователь владельцем сервера
    if server.owner != request.user:
        return JsonResponse({'error': 'Вы не являетесь владельцем сервера'}, status=403)

    server.delete()
    return JsonResponse({'message': 'Сервер успешно удален'}, status=200)


@api_view(['PUT'])
def update_third_party_server(request, server_id):
    """ Обновление данных сервера (PUT) """
    server = get_object_or_404(ThirdPartyServer, id=server_id)

    # Проверяем, что текущий пользователь — владелец сервера
    if server.owner != request.user:
        return JsonResponse({'error': 'Вы не владелец этого сервера'}, status=403)

    print('📌 request.data:', request.data)  # Отладка входящих данных
    print('📌 request.FILES:', request.FILES)  # Отладка загружаемых файлов

    form = ThirdPartyServerForm(request.data, request.FILES, instance=server)  # Учитываем файлы

    if form.is_valid():
        server = form.save()
        return JsonResponse({'success': True, 'data': {'id': server.id, 'description': server.description, 'ip': server.ip, 'port': server.port, 'server_type': server.server_type.id }})

    print('❌ Ошибка при обновлении сервера:', form.errors, form.non_field_errors)
    return JsonResponse({'errors': form.errors.as_json()}, status=400)