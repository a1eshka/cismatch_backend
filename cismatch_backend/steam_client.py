import asyncio
import os
from steampy.client import SteamClient
from steampy.models import Asset, GameOptions



STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USERNAME = os.getenv("STEAM_USERNAME")
STEAM_PASSWORD = os.getenv("STEAM_PASSWORD")
SHARED_SECRET = os.getenv("STEAM_SHARED_SECRET")
IDENTITY_SECRET = os.getenv("STEAM_IDENTITY_SECRET")
STEAM_GUARD_PATH = os.getenv("STEAM_GUARD_PATH")

proxies =  {
    "https": "http://zzraqY:wzTqwz@195.158.193.249:8000"
} 
  
client = SteamClient(STEAM_API_KEY,proxies=proxies) #,proxies=proxies

async def start_bot():
    """Авторизация бота в Steam"""
    try:
        print("🤖 Бот запущен. Ожидание входа в Steam...")
        #session_cookies = [cookie for cookie in client._session.cookies if cookie.name == 'sessionid']
        
        # Удаляем все cookies с таким именем
        #for cookie in session_cookies[1:]:
        #    client._session.cookies.remove(cookie.name)
        await asyncio.to_thread(client.login, STEAM_USERNAME, STEAM_PASSWORD, STEAM_GUARD_PATH)
        print("✅ Успешный вход в Steam!")
        if client.is_session_alive():
            print("✅ Сессия активна, бот авторизован!")
        else:
            print("⚠️ Сессия не активна, возможен разлогин!")
            await asyncio.to_thread(client.login, STEAM_USERNAME, STEAM_PASSWORD, STEAM_GUARD_PATH)
            if client.is_session_alive():
                print("✅ Повторный вход успешен!")
            return False
        
        return True    
    except Exception as e:
        print(f"❌ Ошибка при авторизации: {e}")
        return False


async def create_trade_offer(user_id, asset_id, skin_name, offer_price, trade_url):
    """Создание трейд-оффера с использованием URL (пользователь отдает предмет)"""
    try:
        # Проверяем активность сессии
        print("🕵️‍♂️ Проверяем активность сессии...")
        await start_bot()
        if not client.is_session_alive():
            print("⚠️ Сессия не активна, авторизуем клиента...")
            session_status = await start_bot()
            if not session_status:
                raise Exception("Ошибка: Не удалось авторизовать клиента!")

        print(f"📦 Отправляем запрос на получение {skin_name} от пользователя {user_id}")
        # Определяем предмет, который нам передает пользователь
        game = GameOptions.CS
        item = Asset(asset_id, game)
        items_from_them = [item]  # CS:GO инвентарь
        items_from_me = []  # Мы ничего не отправляем
        trade_offer_url = trade_url
        # Создаем трейд через URL
        trade_response = await asyncio.to_thread(
            client.make_offer_with_url,
            items_from_me,
            items_from_them,
            trade_offer_url,
            message=f"Вы получите {offer_price}руб. за {skin_name}!"
        )
        print(f"Ответ от API трейда: {trade_response}")
        trade_offer_id = trade_response.get("tradeofferid")
        if trade_offer_id:
            print(f"✅ Трейд отправлен! ID: {trade_offer_id}")

            return trade_offer_id
        else:
            raise Exception("❌ Ошибка: трейд не был отправлен!")

    except Exception as e:
        print(f"❌ Ошибка при отправке трейда: {e}")
        return None

# Основной цикл бота
async def main():
    session_status = await start_bot()
    if session_status:
        print("Бот готов к работе!")

if __name__ == "__main__":
    asyncio.run(main())