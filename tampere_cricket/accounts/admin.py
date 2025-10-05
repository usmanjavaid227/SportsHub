from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'experience_level', 'role', 'city')
    list_filter = ('experience_level', 'role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Cricket Information', {
            'fields': ('bio', 'role', 'experience_level', 'preferred_batting_style', 
                      'preferred_bowling_style', 'years_playing', 'phone', 'city', 'avatar')
        }),
    )
