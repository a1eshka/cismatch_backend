from django.urls import path
from .views import run_raffle, get_skins
from . import api

urlpatterns = [
    path('skins/', get_skins, name='get_skins'),  # Список активных скинов
    path('', api.get_raffles, name='get_raffles'),  # Список активных розыгрышей
    path('tickets/buy/<int:skin_id>/', api.buy_ticket, name='buy_ticket'),# Покупка тикета
    path('tickets/count/<uuid:user_id>/<int:raffle_id>/', api.get_ticket_count, name='get_ticket_count'),
    path("tasks/", api.task_list, name="task-list"),
    path("tasks/check/", api.check_task, name="task-check"),
    path('tasks/completed/', api.completed_tasks, name='completed_tasks'),
    path('draw/<int:raffle_id>/', run_raffle, name='run_raffle'),  # Проведение розыгрышаtickets/count/<int:user_id>/<int:raffle_id>/
]