from django.forms import ModelForm

from .models import Post, Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'body',
            'type',
            'status',
            'role',
            'images'
        )

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

