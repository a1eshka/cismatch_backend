from django.urls import path

from . import api

urlpatterns = [
    path('posts/', api.posts_list, name='api_posts_list'),
    path('posts/user/', api.user_posts_list, name='user-posts-list'),
    path('types/', api.types_list, name='api_types_list'),
    path('status/', api.status_list, name='api_status_list'),
    path('role/', api.role_list, name='api_role_list'),
    path('post/create/', api.create_post, name='api_create_post'),
    path('post/<uuid:pk>', api.post_detail, name='api_post_detail'),
    path('post/delete/<uuid:post_id>/', api.delete_post, name='delete_post'),
    path('post/update/<uuid:post_id>/', api.update_post, name='update_post'),
    path('comments/create/<uuid:postId>', api.create_comment, name='create_comment'),
    path('post/<uuid:postId>/comments/', api.list_post_comments, name='list_post_comments'),

]