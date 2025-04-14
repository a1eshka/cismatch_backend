# views.py
import asyncio
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import json
import logging
import sys
from venv import logger
from django.core.cache import cache
import os
from django.views.decorators.csrf import csrf_exempt
# Добавляем корневую папку в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
from server.models import ThirdPartyServer
from steam_client import create_trade_offer, client, start_bot
from yookassa import Configuration, Payment, Payout, SbpBanks
from yookassa.domain.models import Recipient
import uuid
import hmac
import requests
from asgiref.sync import sync_to_async

from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from django.http import JsonResponse
from .models import PromoCode, PromoCodeHistory, SkinBuyOrder, User  # импортируйте вашу модель пользователя
from .serializers import PromoCodeSerializer, SkinBuyOrderSerializer, UserDetailSerializer  # импортируйте сериализатор для пользователя
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
import hashlib


logger = logging.getLogger(__name__)

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])  # Разрешает доступ без токена
def user_info(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return JsonResponse({'data': serializer.data}, json_dumps_params={'ensure_ascii': False}, status=200)

    elif request.method == 'PUT':
        # Разрешаем редактировать только свой профиль
        if request.user.is_authenticated and request.user.id != user.id:
            return JsonResponse({'error': 'You do not have permission to edit this profile.'}, status=403)

        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'data': serializer.data}, json_dumps_params={'ensure_ascii': False}, status=200)
        return JsonResponse({'error': serializer.errors}, status=400)

    
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@parser_classes([MultiPartParser])  # Поддержка файлов
def upload_background(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Проверяем, есть ли файл в запросе
    if 'background' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    # Сохраняем файл в поле background_profile
    user.background_profile = request.FILES['background']
    user.save()

    # Возвращаем URL изображения
    return JsonResponse({'background_profile_url': user.background_profile.url}, status=200)

@api_view(['DELETE'])
@authentication_classes([])
@permission_classes([])
def delete_background(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Проверяем, есть ли фоновое изображение
    if not user.background_profile:
        return JsonResponse({'error': 'Фоновое изображение отсутствует'}, status=400)

    # Удаляем файл из хранилища
    if user.background_profile:
        file_path = user.background_profile.path  # Получаем путь к файлу
        default_storage.delete(file_path)  # Удаляем файл

    # Очищаем поле background_profile
    user.background_profile = None
    user.save()

    return JsonResponse({'message': 'Фоновое изображение успешно удалено'}, status=200)

@api_view(['POST'])
def create_promo_code(request):
    serializer = PromoCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

@api_view(['POST'])
def activate_promo_code(request):
    try:
        # Логируем заголовки и тело запроса
        logger.info(f'Заголовки запроса: {request.headers}')
        logger.info(f'Тело запроса: {request.body}')

        # Используем request.data для автоматического парсинга JSON
        data = request.data
        code = data.get('code')
        user_id = data.get('userId')

        # Проверяем, что код передан
        if not code:
            logger.error('Не указан промокод')
            return JsonResponse({'success': False, 'error': 'Необходимо указать промокод'}, status=400)

        # Ищем промокод в базе данных
        try:
            promo_code = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            logger.error(f'Промокод не найден: {code}')
            return JsonResponse({'success': False, 'error': 'Такого промокода не существует'}, status=404)

        # Проверяем, что срок действия промокода не истек
        if promo_code.is_expired():
            logger.error(f'Срок действия промокода истек: {code}')
            return JsonResponse({'success': False, 'error': 'Срок действия промокода истек'}, status=400)

        # Ищем пользователя в базе данных
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f'Пользователь не найден: {user_id}')
            return JsonResponse({'success': False, 'error': 'Пользователь не найден'}, status=404)

        # Проверяем, не активировал ли пользователь этот промокод ранее
        logger.info(f'Проверка активации промокода: code={code}, user_id={user.id}')
        if PromoCodeHistory.objects.filter(promo_code=promo_code, user=user).exists():
            logger.error(f'Пользователь уже активировал этот промокод: {code}')
            return JsonResponse({'success': False, 'error': 'Вы уже активировали этот промокод'}, status=400)

        # Зачисляем сумму на баланс пользователя
        logger.info(f'Зачисление суммы на баланс пользователя: user_id={user.id}, amount={promo_code.amount}')
        user.balance += promo_code.amount
        user.save()

        # Создаем запись об активации промокода
        logger.info(f'Создание записи об активации промокода: code={code}, user_id={user.id}')
        PromoCodeHistory.objects.create(promo_code=promo_code, user=user)

        logger.info(f'Промокод активирован: code={code}, user_id={user.id}, username={user.username or user.email}, amount={promo_code.amount}')
        return JsonResponse({
            'success': True,  # Указываем, что операция успешна
            'message': 'Промокод успешно активирован',
            'amount': promo_code.amount,
            'user_uuid': str(user.id)  # Передаем UUID пользователя в ответе
        }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        # Логируем ошибку и возвращаем сообщение
        logger.error(f'Ошибка при активации промокода: {e}', exc_info=True)
        return JsonResponse({'success': False, 'error': 'Внутренняя ошибка сервера'}, status=500)

@api_view(['GET'])
def list_promo_codes(request):
    promo_codes = PromoCode.objects.all()
    serializer = PromoCodeSerializer(promo_codes, many=True)
    return JsonResponse(serializer.data)


@api_view(['GET'])
def get_inventory(request, user_id):
    try:
        user = User.objects.get(id=user_id)  # Найти пользователя по переданному user_id
    except User.DoesNotExist:
        return JsonResponse({"error": "Пользователь не найден"}, status=404)

    if not user.steam_id or not user.trade_url:
        return JsonResponse({"error": "Steam ID или Trade URL отсутствует"}, status=400)

    inventory_url = f"https://steamcommunity.com/inventory/{user.steam_id}/730/2?l=russian&count=5000"

    try:
        response = requests.get(inventory_url, timeout=10)
        response.raise_for_status()

        if "application/json" not in response.headers.get("Content-Type", ""):
            return JsonResponse({"error": "Steam API вернул не JSON"}, status=500)

        data = response.json()
        return JsonResponse(data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Ошибка запроса к Steam API: {str(e)}"}, status=500)



CSGO_MARKET_API_URL = "https://market.csgo.com/api/v2/search-list-items-by-hash-name-all"
API_KEY = "Uq5iJBQ8Hn03A284S490v4G8a1qM1fX"  # Укажите ваш API-ключ

@api_view(["POST"])
def get_csgo_market_prices(request):
    try:
        # Проверяем, что request содержит JSON
        if not request.body:
            return JsonResponse({"error": "Пустой запрос"}, status=400)

        # Парсим JSON-данные
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON"}, status=400)

        # Проверяем, что market_hash_names - это список
        market_hash_names = data.get("market_hash_names")
        if not isinstance(market_hash_names, list) or not market_hash_names:
            return JsonResponse({"error": "market_hash_names должен быть непустым списком"}, status=400)

        # Генерируем короткий ключ для кеша с помощью хеширования
        cache_key = 'csgo_market_prices_' + hashlib.md5(' '.join(market_hash_names).encode()).hexdigest()

        # Проверяем, есть ли в кеше сохраненные данные
        cached_prices = cache.get(cache_key)

        if cached_prices:
            # Если данные есть в кеше, возвращаем их
            print(f"Данные взяты из кеша для ключа {cache_key}")
            return JsonResponse({"prices": cached_prices})
        print(f"Данные не найдены в кеше, запрашиваем API для ключа {cache_key}")
        all_prices = {}

        # Разбиваем market_hash_names на группы по 50 предметов
        chunk_size = 50
        for i in range(0, len(market_hash_names), chunk_size):
            chunk = market_hash_names[i:i + chunk_size]

            # Формируем параметры запроса
            params = {
                "key": API_KEY,
                "list_hash_name[]": chunk
            }

            response = requests.get(CSGO_MARKET_API_URL, params=params)
            # Проверяем код ответа
            if response.status_code != 200:
                return JsonResponse({"error": f"Ошибка запроса: {response.status_code}"}, status=500)

            # Проверяем, что ответ API - это JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                return JsonResponse({"error": "Ошибка парсинга JSON. Возможно, API-ключ недействителен."}, status=500)

            # Проверяем успешность запроса
            if not data.get("success"):
                return JsonResponse({"error": data.get("error", "Ошибка API")}, status=500)

            # Обрабатываем данные
            for item_name, listings in data.get("data", {}).items():
                if isinstance(listings, list) and listings:  # Проверяем, что это список с элементами
                    first_listing = listings[0]  # Берём первый объект из списка
                    price = first_listing.get("price", "Цена не найдена")
                    if price != "Цена не найдена":
                        # Уменьшаем цену на 20%
                        price = float(price) * 0.8  # Уменьшаем цену на 20%
                    all_prices[item_name] = {
                        "price": price,
                        "count": first_listing.get("extra", {}).get("volume", "Нет данных"),
                    }
                else:
                    all_prices[item_name] = {"error": "Нет данных по этому предмету"}

        # Сохраняем данные в кеше с временем жизни 1 час (3600 секунд)
        cache.set(cache_key, all_prices, timeout=7200)
        print("TEST CACHE:", cache.get("test_key")) 
        return JsonResponse({"prices": all_prices})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

# Функция для настройки ключей пополнения
def configure_yookassa_for_payments():
    Configuration.account_id = os.environ.get("YOOKASSA_SHOP_ID")
    Configuration.secret_key = os.environ.get("YOOKASSA_SECRET_KEY")

# Функция для настройки ключей вывода
def configure_yookassa_for_payouts():
    Configuration.account_id = os.environ.get("YOOKASSA_PAYOUT_SHOP_ID")
    Configuration.secret_key = os.environ.get("YOOKASSA_PAYOUT_SECRET_KEY")

# URL вашего вебхука
WEBHOOK_URL = "https://putting-ink-russian-nickel.trycloudflare.com/webhook/"

@csrf_exempt
def create_payment(request):
    configure_yookassa_for_payments()
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            print("Тело запроса:", data)  # ✅ Логируем входящие данные
            user = data.get("userId")  # 🔥 Исправляем: должно быть "userId", как в фронтенде
            print("Полученный userId:", user)  # ✅ Проверяем, что userId получен правильно

            amount = data.get("amount")
            description = data.get("description")
            print("FRONT_URL:", os.environ.get("FRONT_URL"))
            if not amount or not description or not user:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            

            # 🏦 Создаем платеж с user_id в metadata
            payment = Payment.create({
                "amount": {
                    "value": amount,
                    "currency": "RUB"
                },
                #    "payment_method_data": {
                #    "type": "sbp"
                #},
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"http://localhost:3000/profile?status=success"
                },
                "capture": True,
                "description": description,
                "metadata": { "user_id": user },  # ✅ Используем userId из запроса
            }, uuid.uuid4())

            return JsonResponse({"confirmation_url": payment.confirmation.confirmation_url})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def create_payment_server(request):
    configure_yookassa_for_payments()
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            print("Тело запроса:", data)  # ✅ Логируем входящие данные
            #user = data.get("userId")  # 🔥 Исправляем: должно быть "userId", как в фронтенде
            server = data.get("serverId")
            days = data.get("days")

            amount = data.get("amount")
            description = data.get("description")
            print("FRONT_URL:", os.environ.get("FRONT_URL"))
            if not amount or not description or not server:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            

            # 🏦 Создаем платеж с user_id в metadata
            payment = Payment.create({
                "amount": {
                    "value": amount,
                    "currency": "RUB"
                },
                #    "payment_method_data": {
                #    "type": "sbp"
                #},
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"http://localhost:3000/servers"
                },
                "capture": True,
                "description": description + ' ' + server,
                "metadata": { "server_id": server, "days": days },  # ✅ Используем serverId из запроса
            }, uuid.uuid4())

            return JsonResponse({"confirmation_url": payment.confirmation.confirmation_url})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def create_payout(request):
    configure_yookassa_for_payouts()  # 🏦 Настраиваем API для выплат

    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)

        user_id = data.get("user_id")
        order_id = data.get("order_id")
        bank_id = data.get('bank_id')
        phone = data.get('phone')

        if not user_id or not order_id:
            return JsonResponse({"error": "user_id и order_id обязательны"}, status=400)

        # 🔎 Проверяем, существует ли такой ордер
        try:
            order = SkinBuyOrder.objects.get(id=order_id, user_id=user_id, status="accepted")
        except SkinBuyOrder.DoesNotExist:
            return JsonResponse({"error": "Заказ не найден или неверный статус"}, status=404)

        # 🔹 Создаем выплату через YooKassa
        payout = Payout.create({
            "amount": {
                "value": str(order.offer_price),  # 💰 Сумма выплаты
                "currency": "RUB"
            },
            "recipient": Recipient(account_id=user_id),
            "payout_destination_data": {
                #"type": "sbp",
                "type": 'yoo_money',
                "account_number": "4100116075156746"
                #"phone": phone,
                #"bank_id": bank_id
            },
            "description": f"Выплата за {order.skin_name}, Выплата № {order_id}",
        })

        # ✅ Сохраняем ссылку на выплату в order
        order.payment_url = payout.id
        order.status = "bought"  # 💰 Меняем статус на "Выкуплено"
        order.save()

        return JsonResponse({"message": "Выплата создана", "payment_url": payout.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Ошибка обработки JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка: {str(e)}"}, status=500)

@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def payout_webhook(request):
    """Обрабатывает статус платежа от YooKassa"""
    payload = json.loads(request.body)
    payment_id = payload.get("object", {}).get("id")
    status = payload.get("object", {}).get("status")

    if not payment_id or not status:
        return JsonResponse({"error": "Некорректный вебхук"}, status=400)

    # Ищем ордер по payment_url
    try:
        order = SkinBuyOrder.objects.get(payment_url__contains=payment_id)
    except SkinBuyOrder.DoesNotExist:
        return JsonResponse({"error": "Ордер не найден"}, status=400)

    # Если платеж успешен, обновляем статус
    if status == "succeeded":
        order.status = "bought"
        order.save()
        return JsonResponse({"message": "Платеж успешно обработан"}, status=200)

    return JsonResponse({"message": "Платеж в ожидании или отклонен"}, status=200)

@csrf_exempt
def get_sbp_banks(request):
    configure_yookassa_for_payouts()
    """Получение списка банков СБП через YooKassa SDK"""
    try:
        # Запрос списка банков через YooKassa SDK
        banks = SbpBanks.list()  # Предположим, что этот метод возвращает список банок

        # Преобразуем ответ в требуемый формат
        bank_list = [
            {
                "bank_id": bank.get("id"),
                "name": bank.get("name"),
                "bic": bank.get("bic")
            }
            for bank in banks
        ]

        # Формируем итоговый ответ
        response_data = {
            "type": "list",
            "items": bank_list
        }

        # Логируем результат
        logger.info('Received banks list: %s', bank_list)

        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        # Логируем ошибку
        logger.error('Error occurred while fetching banks: %s', str(e))

        return JsonResponse({'error': f'Ошибка: {str(e)}'}, status=500)

    
@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            print("Webhook received:", body)  # ✅ Логируем вебхук

            data = json.loads(body)
            event_type = data.get('event')

            if event_type == 'payment.succeeded':
                payment = data.get('object')
                amount = Decimal(payment['amount']['value'])
                metadata = payment.get('metadata', {})

                server_id = metadata.get("server_id")
                days_paid = int(metadata.get("days", 0))  # ✅ Приводим `days` к числу
                user_id = metadata.get("user_id")

                if server_id and days_paid:
                    # 🔹 Поднятие сервера
                    try:
                        print(f"Trying to find server {server_id}")  # ✅ Лог перед поиском сервера
                        server = ThirdPartyServer.objects.get(id=server_id)
                        server.is_paid = True
                        server.is_boosted = True
                        if server.boost_expires_at:
                            # Если boost_expires_at уже есть, прибавляем дни
                            server.boost_expires_at += timedelta(days=days_paid)
                        else:
                            # Если boost_expires_at пустое, устанавливаем дату как текущую + дни
                            server.boost_expires_at = timezone.now() + timedelta(days=days_paid)
                        server.save()
                        print(f"Server {server_id} boosted for {days_paid} days")  # ✅ Лог успеха
                        return JsonResponse({'message': 'Server boost updated successfully'})
                    except ThirdPartyServer.DoesNotExist:
                        return JsonResponse({'error': 'Server not found'}, status=404)

                elif user_id:
                    # 🔹 Пополнение баланса
                    try:
                        user = User.objects.get(id=user_id)
                        user.balance += amount
                        user.save()
                        print(f"User {user_id} balance updated: +{amount} RUB")  # ✅ Лог успеха
                        return JsonResponse({'message': 'Balance updated successfully'})

                    except User.DoesNotExist:
                        return JsonResponse({'error': 'User not found'}, status=404)

                return JsonResponse({'error': 'Invalid payment metadata'}, status=400)

            return JsonResponse({'error': 'Unhandled event type'}, status=400)

        except Exception as e:
            print("Webhook error:", str(e))  # ✅ Лог ошибки
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)




def is_valid_signature(payload, signature):
    expected_signature = generate_signature(payload)
    return expected_signature == signature

def generate_signature(payload):
    secret_key = os.environ.get("YOOKASSA_SECRET_KEY").encode('utf-8')
    return hmac.new(secret_key, payload, hashlib.sha256).hexdigest()

def handle_successful_payment(payment_id):
    print(f"Payment {payment_id} succeeded")

def handle_canceled_payment(payment_id):
    print(f"Payment {payment_id} canceled")

@csrf_exempt
async def sell_item(request):
    """Создание трейд-оффера по запросу клиента"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data["user_id"]
            asset_id = data["asset_id"]
            skin_name = data["skin_name"]
            offer_price = data["offer_price"]
            trade_url = data["trade_url"] 
            image_url = data["image_url"]


            # Создаем запись в БД
            order = await sync_to_async(SkinBuyOrder.objects.create)(
                user_id=user_id,
                asset_id=asset_id,
                skin_name=skin_name,
                offer_price=offer_price,
                image_url=image_url,
                status="pending",
            )

            async def process_trade():
                """Асинхронная отправка трейда и обновление статуса"""
                await asyncio.sleep(2)  # Задержка перед началом работы

                trade_offer_id = await create_trade_offer(user_id, asset_id, skin_name, offer_price, trade_url)

                if trade_offer_id:
                    order.trade_offer_id = trade_offer_id
                    order.status = "approved"
                    await sync_to_async(order.save)()
                    return JsonResponse({"success": True, "trade_offer_id": trade_offer_id})
                else:
                    order.status = "rejected"
                    await sync_to_async(order.save)()
                    return JsonResponse({"success": False, "error": "Ошибка при отправке трейд-оффера"}, status=500)

            # Запускаем процесс трейда в фоне
            await process_trade()

            return JsonResponse({"success": True, "message": "Трейд создается!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([])  # Отключаем аутентификацию для тестов
@permission_classes([])  # Отключаем проверки прав
def user_orders_list(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'user_id не указан'}, status=400)

    orders = SkinBuyOrder.objects.filter(user_id=user_id)

    serializer = SkinBuyOrderSerializer(orders, many=True)
    return JsonResponse({'data': serializer.data}, json_dumps_params={'ensure_ascii': False})