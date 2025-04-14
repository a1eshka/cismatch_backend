from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Skin, Raffle
from django.utils import timezone


def run_raffle(raffle_id):
    try:
        raffle = Raffle.objects.get(id=raffle_id)

        # Если розыгрыш уже завершен
        if raffle.is_drawn:
            return JsonResponse({'error': 'Raffle has already been drawn'}, status=400)

        # Если розыгрыш еще не завершен по времени
        if raffle.end_time > timezone.now():
            return JsonResponse({'error': 'Raffle has not ended yet'}, status=400)

        # Проведение розыгрыша
        raffle.draw_winner()
        return JsonResponse({'message': f'Winner: {raffle.winner.username}'})
    
    except Raffle.DoesNotExist:
        return JsonResponse({'error': 'Raffle not found'}, status=404)
    
def get_skins(request):
    skins = Skin.objects.filter(is_active=True)
    skin_data = [{'id': skin.id, 'name': skin.name, 'price_in_tickets': skin.price_in_tickets ,'image_url': skin.image_url} for skin in skins]
    data = {'data': skin_data}
    return JsonResponse(data, safe=False)


