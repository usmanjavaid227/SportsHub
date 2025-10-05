from django.contrib import admin
from django.utils.html import format_html
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'published_at', 'created_at', 'preview_link')
    list_filter = ('published', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('published', 'published_at', 'author')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_link(self, obj):
        if obj.published:
            return format_html(
                '<a href="/news/" target="_blank" style="color: green;">View on Site</a>'
            )
        return format_html('<span style="color: red;">Not Published</span>')
    preview_link.short_description = 'Status'
