import os
import time
import json
import base64
import hmac
import struct
import traceback
import requests
from steam.guard import SteamAuthenticator
from hashlib import sha1
import steam.webauth as wa
from .models import SkinBuyOrder,User
from steam.steamid import SteamID

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USERNAME = os.getenv("STEAM_USERNAME")
STEAM_PASSWORD = os.getenv("STEAM_PASSWORD")
SHARED_SECRET = os.getenv("STEAM_SHARED_SECRET")
IDENTITY_SECRET = os.getenv("STEAM_IDENTITY_SECRET")

def generate_steam_guard_code(shared_secret):
    """Генерирует 2FA-код для входа в Steam"""
    timestamp = int(time.time()) // 30  # Steam использует 30-секундные интервалы
    hmac_generator = hmac.new(base64.b64decode(shared_secret), struct.pack(">Q", timestamp), sha1)
    hmac_hash = hmac_generator.digest()
    
    start = hmac_hash[19] & 0x0F
    full_code = struct.unpack(">I", hmac_hash[start:start + 4])[0] & 0x7FFFFFFF

    chars = "23456789BCDFGHJKMNPQRTVWXY"
    code = ""

    for _ in range(5):
        code += chars[full_code % len(chars)]
        full_code //= len(chars)

    return code

def steam_login():
    """Авторизация в Steam с использованием steam.webauth"""
    try:
        print(f"🔹 Попытка авторизации для пользователя {STEAM_USERNAME}...")
        auth = wa.WebAuth(STEAM_USERNAME)

        # 🔸 Попытка входа с паролем
        print("🔹 Вход с паролем...")
        session = auth.login(STEAM_PASSWORD)

    except wa.TwoFactorCodeRequired:
        print("🔹 Требуется 2FA-код. Генерируем...")
        guard_code = generate_steam_guard_code(SHARED_SECRET)
        print(f"🔹 2FA-код: {guard_code}")

                # 🔹 Повторный вход с 2FA-кодом
        try:
            session = auth.login(twofactor_code=guard_code)
        except KeyError:
            print("❌ Ошибка: Steam не вернул необходимые данные, попробуйте снова.")
            return None, None

    except wa.EmailCodeRequired:
        print("❌ Требуется код подтверждения из email. Проверьте почту и повторите попытку.")
        return None, None

    except wa.CaptchaRequired:
        print("❌ Требуется ввод капчи. Вход невозможен в автоматическом режиме.")
        return None, None

    except wa.LoginIncorrect:
        print("❌ Ошибка: Неправильный логин или пароль.")
        return None, None

    except Exception as e:
        print(f"❌ Ошибка при авторизации в Steam: {e}")
        return None, None

    # 🔹 Проверяем, что сессия активна
    if session and hasattr(session, "cookies") and "sessionid" in session.cookies:
        print("✅ Успешный вход в Steam!")
        sessionid = session.cookies["sessionid"]
        cookies = session.cookies.get_dict()
        print(f"🔹 SESSION ID: {sessionid}")
        print(f"🔹 Cookies: {cookies}")
        return sessionid, cookies
    else:
        print("❌ Ошибка: Steam не передал корректные данные.")
        return None, None
    

def create_trade_offer(user_id, asset_id, skin_name, offer_price, image_url):
    """Отправляет трейд-оффер пользователю"""
    result = steam_login()  # Получаем результат функции steam_login
    if result is None:
        print("❌ Ошибка: steam_login() вернул None")
        return None  # Вернем None, если login не удалось

    session_id, cookies = result  # Распаковываем только если нет ошибки
    print('result:', result)
    user = User.objects.get(id=user_id)  # Получаем пользователя
    steam64_id = user.steam_id
    steamid32 = SteamID(steam64_id).as_32
    steam_id = steamid32
    print('steamid:', steam_id)

    trade_offer_data = {
        "sessionid": session_id,
        "serverid": "1",
        "partner": steam_id,
        "tradeoffermessage": f"Продажа {skin_name} за {offer_price} ₽",
        "json_tradeoffer": json.dumps({
            "newversion": True,
            "version": 2,
            "me": {
                "assets": [{"appid": 730, "contextid": "2", "assetid": asset_id}],
                "currency": [],
                "ready": False,
            },
            "them": {
                "assets": [],
                "currency": [],
                "ready": False,
            },
        }),
        "trade_offer_create_params": json.dumps({}),
        "captcha": "",
    }

    headers = {
        "Referer": f"https://steamcommunity.com/tradeoffer/new/?partner={steam_id}",
        "Origin": "https://steamcommunity.com",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(
        "https://steamcommunity.com/tradeoffer/new/send",
        data=trade_offer_data,
        headers=headers,
        cookies=cookies,
    )

    if response.status_code == 200:
        trade_offer_id = response.json().get("tradeofferid")
        print(f"✅ Трейд-оффер отправлен! ID: {trade_offer_id}")

        # Записываем в базу
        SkinBuyOrder.objects.create(
            user=user,
            asset_id=asset_id,
            skin_name=skin_name,
            offer_price=offer_price,
            trade_offer_id=trade_offer_id,
            image_url=image_url,
            status="pending"
        )

        confirm_trade_offer(cookies)  # Автоподтверждение
        return trade_offer_id
    else:
        print(f"❌ Ошибка отправки трейда: {response.text}")
        return None

def generate_confirmation_key(identity_secret, tag="conf"):
    """Генерирует ключ подтверждения трейдов"""
    timestamp = int(time.time())
    hmac_generator = hmac.new(base64.b64decode(identity_secret), struct.pack(">Q", timestamp) + tag.encode(), sha1)
    return base64.b64encode(hmac_generator.digest()).decode()

def confirm_trade_offer(cookies):
    """Автоматически подтверждает трейды"""
    sessionid = cookies.get("sessionid")
    steamid = cookies.get("steamLoginSecure").split("%7C%7C")[0]
    
    confirmation_key = generate_confirmation_key(IDENTITY_SECRET, "conf")
    url = f"https://steamcommunity.com/mobileconf/conf"
    
    params = {
        "p": "android",
        "a": steamid,
        "k": confirmation_key,
        "t": int(time.time()),
        "m": "android",
        "tag": "conf",
    }

    headers = {"Referer": "https://steamcommunity.com/mobileconf"}

    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    if response.status_code == 200:
        print("✅ Трейд успешно подтвержден!")
        return True
    else:
        print("❌ Ошибка подтверждения трейда")
        return False
