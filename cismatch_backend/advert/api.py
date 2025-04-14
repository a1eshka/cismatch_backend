from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import Advert, MiniNews
from .serializers import AdvertListSerializer, MiniNewsListSerializer

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def advert_list(request):
    adverts = Advert.objects.all()
    serializer = AdvertListSerializer(adverts, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def mininews_list(request):
    mininews = MiniNews.objects.all()
    serializer = MiniNewsListSerializer(mininews, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})