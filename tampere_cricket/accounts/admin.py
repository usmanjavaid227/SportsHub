from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'city', 'is_deleted', 'deleted_at')
    list_filter = ('role', 'is_staff', 'is_active', 'is_deleted')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Cricket Information', {
            'fields': ('role', 'preferred_batting_style', 'preferred_bowling_style', 'phone', 'city', 'avatar')
        }),
        ('Soft Delete Information', {
            'fields': ('is_deleted', 'deleted_at', 'deleted_reason'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('deleted_at',)
    
    actions = ['restore_users', 'hard_delete_users']
    
    def restore_users(self, request, queryset):
        """Restore soft-deleted users"""
        restored_count = 0
        for user in queryset.filter(is_deleted=True):
            user.restore()
            restored_count += 1
        
        self.message_user(request, f'{restored_count} users have been restored.')
    restore_users.short_description = "Restore selected users"
    
    def hard_delete_users(self, request, queryset):
        """Permanently delete users (use with caution)"""
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{deleted_count} users have been permanently deleted.')
    hard_delete_users.short_description = "Permanently delete selected users"
    
    def get_queryset(self, request):
        """Show all users including soft-deleted ones"""
        return super().get_queryset(request)
