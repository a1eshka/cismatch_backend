import os
import django
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from django.core.wsgi import get_wsgi_application
from .lifespan import lifespan  # Подключаем lifespan

# Загружаем Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cismatch_backend.settings')
django.setup()

# Django ASGI приложение
django_asgi_app = get_asgi_application()

# FastAPI-приложение с lifespan для запуска бота в фоне
fastapi_app = FastAPI(lifespan=lifespan)

# Монтируем Django API как WSGI middleware на корневой путь
fastapi_app.mount("/", WSGIMiddleware(get_wsgi_application()))

# Монтируем FastAPI-приложение на путь /fastapi
@fastapi_app.get("/fastapi")
async def fastapi_root():
    return {"message": "FastAPI работает!"}

# Устанавливаем основной ASGI-приложение как FastAPI с ботом
application = django_asgi_app  # Основное приложение — FastAPI с ботом
