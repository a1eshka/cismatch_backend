import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .forms import CommentForm, PostForm
from .models import Post, Role, Status, TypePost, Comment
from .serializers import CommentSerializer, PostsDetailSerializer, PostsListSerializer, StatusListSerializer, TypePostListSerializer

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def posts_list(request):
    posts = Post.objects.all()
    serializer = PostsListSerializer(posts, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['DELETE'])
def delete_post(request, post_id):
    """
    API для удаления поста из базы данных.
    Удаляет пост только если текущий пользователь является его владельцем.
    """
    post = get_object_or_404(Post, id=post_id)

    # Проверяем, является ли текущий пользователь владельцем поста
    if post.author != request.user:
        return JsonResponse({'error': 'Вы не являетесь владельцем поста'}, status=403)

    post.delete()
    return JsonResponse({'message': 'Пост успешно удален'}, status=200)


@api_view(['PUT'])
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print('📌 request.data:', request.data)  # <- Покажет, что пришло в JSON
    print('📌 request.FILES:', request.FILES)
    form = PostForm(request.data, request.FILES, instance=post)  # ✅ Добавили request.FILES

    if form.is_valid():
        post = form.save()
        return JsonResponse({'success': True, 'data': post.id})

    print('❌ Ошибка при обновлении поста:', form.errors, form.non_field_errors)
    return JsonResponse({'errors': form.errors.as_json()}, status=400)
    
    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def user_posts_list(request):
    user_id = request.GET.get('user_id')

    if user_id:
        posts = Post.objects.filter(author_id=user_id)  
    else:
        posts = Post.objects.all()  

    serializer = PostsListSerializer(posts, many=True)
    return JsonResponse({'data': serializer.data}, json_dumps_params={'ensure_ascii': False})


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def post_detail(request, pk):
    post = Post.objects.get(pk=pk)
    post.increment_views()  # Увеличиваем количество просмотров
    serializer = PostsDetailSerializer(post, many=False)
    data = serializer.data
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def types_list(request):
    types = TypePost.objects.all()
    serializer = TypePostListSerializer(types, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['POST', 'FILES'])
def create_post(request):
    form = PostForm(request.data, request.FILES)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return JsonResponse({'success': True, 'data': post.id})
    
    else:
        print('error', form.errors, form.non_field_errors)
        return JsonResponse({'errors': form.errors.as_json()}, status=400)
    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def status_list(request):
    status = Status.objects.all()
    serializer = StatusListSerializer(status, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def role_list(request):
    roles = Role.objects.all()
    serializer = StatusListSerializer(roles, many=True)
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})

@api_view(['POST'])
def create_comment(request, postId):
    post = get_object_or_404(Post, id=postId)  # Получаем пост по ID
    form = CommentForm(request.data)  # Используем request.data для получения данных

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post  # Привязываем комментарий к посту
        comment.author = request.user  # Устанавливаем автора комментария
        comment.save()

        return JsonResponse({'success': True, 'data': comment.id}, status=201)

    else:
        print('error', form.errors, form.non_field_errors)
        return JsonResponse({'errors': form.errors.as_json()}, status=400)
    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def list_post_comments(request, postId):
    post = Post.objects.get(id=postId)  # Получаем пост по id
    comments = Comment.objects.filter(post=post)  # Фильтруем комментарии по посту
    serializer = CommentSerializer(comments, many=True)  # Сериализуем комментарии
    data = {'data': serializer.data}
    return JsonResponse(data, json_dumps_params={'ensure_ascii':False})    
