from django.contrib import admin

from .models import Post,Status,Role,TypePost,Comment

admin.site.register(Post)

@admin.register(TypePost)
class TypePostAdmin (admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Status)
class StatusAdmin (admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Role)
class StatusAdmin (admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Comment)
