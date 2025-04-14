import logging
from datetime import timedelta
import time
from celery import shared_task
from .models import SkinBuyOrder
from steam_client import client
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def check_trade_status():
    """Проверяем отправленные трейды"""
    for attempt in range(3):  # Делаем 3 попытки
        trade_offers = client.get_trade_offers(get_sent_offers=True)
        print(f"📩 Попытка {attempt+1}. Ответ API:", trade_offers)

        if "response" in trade_offers and "trade_offers_sent" in trade_offers["response"]:
            sent_trades = trade_offers["response"]["trade_offers_sent"]
            
            for trade in sent_trades:
                trade_id = trade["tradeofferid"]
                state = trade["trade_offer_state"]
                print(f"🔎 Трейд {trade_id}: статус {state}")

            return sent_trades  # Возвращаем список трейдов

        print("⚠️ Ошибка: Не удалось получить список трейдов! Ждем 5 секунд и пробуем снова...")
        time.sleep(5)

    return []  # Если после 3 попыток не получилось — возвращаем пустой список


@shared_task
def reject_old_approved_orders():
    """
    Проверяет ордера, которые более 24 часов находятся в статусе 'approved',
    и переводит их в статус 'rejected'.
    """
    time_threshold = timezone.now() - timedelta(hours=24)

    # Находим заказы в статусе "approved", созданные более 24 часов назад
    old_orders = SkinBuyOrder.objects.filter(status="approved", created_at__lte=time_threshold)

    if old_orders.exists():
        count = old_orders.update(status="rejected")
        logger.info(f"⏳ Автоматически отклонено {count} просроченных ордеров.")
    else:
        logger.info("✅ Нет просроченных ордеров для отклонения.")
        
        
        
#@shared_task
#def send_trade_offer(user_id, asset_id, skin_name, offer_price, trade_url):
#    """Отправка трейд-оффера через Celery"""

    # Проверяем активность сессии
#    if not client.is_session_alive():
#        print("⚠️ Сессия не активна, пробуем авторизоваться...")
#
        # Используем asyncio для асинхронной авторизации
#        login_status = asyncio.run(start_bot())  # Запускаем бота асинхронно

#        if not login_status:
#            print("❌ Ошибка: не удалось авторизоваться!")
#            return "Ошибка авторизации"

    # Создаем трейд
#    result = create_trade_offer(user_id, asset_id, skin_name, offer_price, trade_url)
#    return result