import os
from celery import Celery
import asyncio
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cismatch_backend.settings')

app = Celery('cismatch_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Объединяем все периодические задачи в ОДНОМ месте
app.conf.beat_schedule = {
    "check_trade_status_task": {
        "task": "useraccount.tasks.check_trade_status",
        "schedule": crontab(minute="*/2"),  # Каждые 2 минуты
        "options": {"countdown": 15}
    },
    "run_raffle_check_every_minute": {
        "task": "raffle.tasks.check_and_draw_raffles",
        "schedule": crontab(minute="*/2"),  # Каждую 2 минуты
    },
    'reject_old_orders_every_hour': {
        'task': 'useraccount.tasks.reject_old_approved_orders',
        'schedule': crontab(minute=0, hour='*'),  # Запуск каждый час
    },
}

app.autodiscover_tasks()
# Функция для запуска асинхронных задач в Celery
def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    if loop.is_running():  # Если уже есть event loop (например, в Uvicorn)
        return asyncio.ensure_future(func(*args, **kwargs))
    else:
        return loop.run_until_complete(func(*args, **kwargs))