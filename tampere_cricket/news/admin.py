from django.contrib import admin
from django.utils.html import format_html
from .models import News, NewsCategory


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'published', 'published_at', 'created_at', 'preview_link')
    list_filter = ('published', 'category', 'created_at', 'author')
    search_fields = ('title', 'content', 'excerpt')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'category')
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
                '<a href="/news/" target="_blank" style="color: green;">View Highlights on Site</a>'
            )
        return format_html('<span style="color: red;">Not Published</span>')
    preview_link.short_description = 'Status'


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_preview', 'article_count')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            obj.color,
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def article_count(self, obj):
        count = obj.news_articles.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 12px; font-size: 12px;">{}</span>',
            count
        )
    article_count.short_description = 'Articles'
