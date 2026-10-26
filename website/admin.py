from django.contrib import admin
from django.db.models import Case, IntegerField, Value, When

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'published_at', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    ordering = (
        Case(
            When(status=Post.Status.PUBLISHED, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        'published_at',
        'created_at',
    )
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'excerpt', 'body')}),
        ('Publishing', {'fields': ('status', 'published_at')}),
        ('History', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
