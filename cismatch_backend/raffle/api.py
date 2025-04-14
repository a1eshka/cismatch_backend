import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .serializers import TaskSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import Skin, Task, Ticket, Raffle, UserTask
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

@api_view(['POST'])
def buy_ticket(request, skin_id):
    user = request.user  # Получаем текущего пользователя
    skin = get_object_or_404(Skin, id=skin_id)

    # Получаем розыгрыш, связанный с этим скином
    raffle = get_object_or_404(Raffle, skin=skin)

    # Проверка, что скин доступен для покупки
    if not skin.is_active:
        return JsonResponse({'error': 'This skin is no longer available'}, status=400)

    # Проверка наличия средств для покупки тикетов
    if user.balance < skin.price_in_tickets:
        return JsonResponse({'error': 'Not enough balance'}, status=400)

    # Проверка, есть ли доступные тикеты в розыгрыше
    if raffle.remaining_tickets <= 0:
        return JsonResponse({'error': 'No tickets left for this skin'}, status=400)

    # Списываем средства с баланса пользователя
    user.balance -= skin.price_in_tickets
    user.save()

    # Создаем тикет для пользователя и сохраняем его UUID
    Ticket.objects.create(user=user, raffle=raffle)

    # Обновляем оставшиеся тикеты в розыгрыше
    raffle.remaining_tickets -= 1
    raffle.save()

    return JsonResponse({
        'message': 'Ticket purchased successfully',
        'remaining_tickets': raffle.remaining_tickets,
        'user_uuid': str(user.id)  # Передаем UUID пользователя в ответе
    }, json_dumps_params={'ensure_ascii':False})


@api_view(['GET'])
@authentication_classes([])  # Без аутентификации
@permission_classes([])  # Без разрешений
def get_ticket_count(request, user_id, raffle_id):
    user = get_object_or_404(User, id=user_id)  # Получаем пользователя по его ID (UUID)
    raffle = get_object_or_404(Raffle, id=raffle_id)  # Получаем розыгрыш по ID

    # Подсчитываем количество билетов для этого пользователя и розыгрыша
    ticket_count = Ticket.objects.filter(user=user, raffle=raffle).count()

    # Возвращаем количество билетов
    return JsonResponse({'ticket_count': ticket_count})

@api_view(['GET'])
@authentication_classes([])  # Оставляем пустые классы аутентификации
@permission_classes([])  # Оставляем пустые классы разрешений
def get_raffles(request):
    user = request.user  # Получаем текущего пользователя

    # Получаем все розыгрыши
    raffles = Raffle.objects.all()
    raffles_data = []

    for raffle in raffles:
        # Подсчитываем количество билетов пользователя для этого розыгрыша
        if user.is_authenticated:
            user_tickets = Ticket.objects.filter(user=user, raffle=raffle).count()
        else:
            user_tickets = 0  # Если пользователь не авторизован, количество билетов будет 0
        winner_name = None
        winner_id = None
        winner_steam_avatar = None
        if raffle.is_drawn and raffle.winner:
            winner_name = raffle.winner.name
            winner_id = raffle.winner.id
            winner_steam_avatar = raffle.winner.steam_avatar

        raffles_data.append({
            'id': raffle.id,
            'skin_id': raffle.skin.id,
            'skin_name': raffle.skin.name,
            'skin_description': raffle.skin.description,
            'image_url': raffle.skin.image_url,
            'price_in_tickets': raffle.skin.price_in_tickets,
            'total_tickets': raffle.total_tickets,
            'remaining_tickets': raffle.remaining_tickets,
            'start_time': raffle.start_time,
            'end_time': raffle.end_time,
            'is_drawn': raffle.is_drawn,
            'winner': winner_name,
            'winner_id': winner_id,
            'winner_steam_avatar': winner_steam_avatar,
            'user_tickets': user_tickets,  # Показываем количество билетов (или 0 для неавторизованных)
        })

    return JsonResponse({'data': raffles_data}, json_dumps_params={'ensure_ascii':False})

@api_view(['POST'])
def check_task(request):
    body = request.body.decode('utf-8')
    data = json.loads(body)
    user = data.get("userId")
    task_id = data.get("taskId")
    user = request.user

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Задание не найдено"}, status=404)

    # Проверяем, выполнял ли пользователь это задание
    user_task = UserTask.objects.filter(user=user, task=task).order_by('-completed_at').first()

    # **Если задание ежедневное (`daily`)**
    if task.task_type == "daily":
        if user_task and user_task.completed_at and user_task.completed_at.date() == now().date():
            return JsonResponse({"error": "Вы уже выполняли это задание сегодня"}, status=400)
        
        UserTask.objects.create(user=user, task=task, completed=True, completed_at=now())
        user.balance += task.reward
        user.save()

        return JsonResponse({"success": f"Вы получили {task.reward} ₽ за ежедневное задание!"})

    # **Если задание на изменение имени**
    elif task.task_type == "username":
        if "cismatch.ru" in user.name:
            if user_task and user_task.completed:
                return JsonResponse({"error": "Вы уже выполняли это задание"}, status=400)

            UserTask.objects.create(user=user, task=task, completed=True, completed_at=now())
            user.balance += task.reward
            user.save()

            return JsonResponse({"success": f"Вы получили {task.reward} ₽ за изменение имени!"})
        return JsonResponse({"error": "Ваше имя не содержит 'cismatch.ru'"}, status=400)

    # **Если задание подписка (`subscribe`)**
    elif task.task_type == "subscribe":
        if user_task and user_task.completed:
            return JsonResponse({"error": "Вы уже выполняли это задание"}, status=400)

        # Засчитываем подписку
        UserTask.objects.create(user=user, task=task, completed=True, completed_at=now())
        user.balance += task.reward
        user.save()

        # Перенаправляем на URL подписки
        return JsonResponse({"success": f"Вы получили {task.reward} ₽ за подписку!", "redirect_url": task.condition}, status=200)

    # **Если кастомное задание**
    elif task.task_type == "custom":
        return JsonResponse({"info": "Пользователь должен выполнить специальное условие"}, status=200)

    return JsonResponse({"error": "Неизвестный тип задания"}, status=400)

@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return JsonResponse(serializer.data, safe=False, json_dumps_params={'ensure_ascii':False})


@api_view(['GET'])
def completed_tasks(request):
    user = request.user
    user_tasks = UserTask.objects.filter(user=user)

    completed_list = []
    today = now().date()

    for user_task in user_tasks:
        completed_list.append({
            "id": user_task.task.id,
            "isDaily": user_task.task.task_type == "daily",
            "completedToday": user_task.completed_at.date() == today if user_task.task.task_type == "daily" else True
        })

    return JsonResponse({"completedTasks": completed_list})