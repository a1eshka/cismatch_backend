from django.http import JsonResponse

from useraccount.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from .forms import TeamForm
from .models import Team
from .serializers import TeamListSerializer
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def teams_list(request):
    teams = Team.objects.all()
    serializer = TeamListSerializer(teams, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def team_detail(request, pk):
    team = Team.objects.get(pk=pk)
    serializer = TeamListSerializer(team, many=False)
    data = serializer.data
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['POST', 'FILES'])
def create_team(request):
    form = TeamForm(request.POST, request.FILES)

    if form.is_valid():
        team = form.save(commit=False)
        team.author = request.user
        team.teammates = request.user
        team.save()

        return JsonResponse({'success': True, 'data': team.id})
    
    else:
        print('error', form.errors, form.non_field_errors)
        return JsonResponse({'errors': form.errors.as_json()}, status=400)

@api_view(['POST'])
def join_team(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        user = request.user

        if user in team.teammates.all():
            # Если пользователь уже в команде, удаляем его (выход из команды)
            team.teammates.remove(user)
            return JsonResponse({'message': 'Вы вышли из команды.'}, status=status.HTTP_200_OK)
        else:
            # Если пользователя нет в команде, добавляем его (вступление в команду)
            team.teammates.add(user)
            return JsonResponse({'message': 'Вы вступили в команду.'}, status=status.HTTP_201_CREATED)