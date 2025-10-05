from django.contrib import admin
from .models import Ground


@admin.register(Ground)
class GroundAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'location')
