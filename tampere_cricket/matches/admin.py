from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django import forms
from .models import Challenge, TimeSlot, MatchResult
from tampere_cricket.grounds.models import Ground
from datetime import date, time, timedelta


class BulkTimeSlotForm(forms.Form):
    """Form for bulk creating time slots"""
    ground = forms.ModelChoiceField(queryset=Ground.objects.all(), required=True)
    start_date = forms.DateField(required=True, help_text="Start date for time slots")
    end_date = forms.DateField(required=True, help_text="End date for time slots")
    time_slots = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter time slots in format: HH:MM-HH:MM:Price (one per line)\nExample:\n09:00-11:00:50.00\n11:00-13:00:60.00",
        required=True
    )


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('challenger', 'opponent', 'ground', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'ground')
    search_fields = ('challenger__username', 'opponent__username', 'ground__name')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('ground', 'date', 'start_time', 'end_time', 'is_available', 'price', 'challenge_count')
    list_filter = ('is_available', 'date', 'ground')
    search_fields = ('ground__name',)
    ordering = ('date', 'start_time')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Time Slot Details', {
            'fields': ('ground', 'date', 'start_time', 'end_time', 'price', 'is_available')
        }),
        ('Availability Info', {
            'fields': ('challenge_count',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('challenge_count',)
    
    def challenge_count(self, obj):
        """Show number of challenges for this time slot"""
        if obj.pk:
            from datetime import datetime
            challenges = Challenge.objects.filter(
                scheduled_at__date=obj.date,
                scheduled_at__time__gte=obj.start_time,
                scheduled_at__time__lt=obj.end_time,
                status__in=['OPEN', 'PENDING', 'ACCEPTED']
            ).count()
            return f"{challenges} challenges"
        return "0 challenges"
    challenge_count.short_description = "Active Challenges"
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        return super().get_queryset(request).select_related('ground')
    
    def get_urls(self):
        """Add custom URLs for bulk operations"""
        urls = super().get_urls()
        custom_urls = [
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_timeslots), name='matches_timeslot_bulk_create'),
        ]
        return custom_urls + urls
    
    def bulk_create_timeslots(self, request):
        """Bulk create time slots for multiple dates"""
        if request.method == 'POST':
            form = BulkTimeSlotForm(request.POST)
            if form.is_valid():
                ground = form.cleaned_data['ground']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                time_slots_text = form.cleaned_data['time_slots']
                
                # Parse time slots
                time_slots = []
                for line in time_slots_text.strip().split('\n'):
                    if ':' in line and '-' in line:
                        try:
                            time_range, price = line.strip().split(':')
                            start_time_str, end_time_str = time_range.split('-')
                            time_slots.append({
                                'start_time': time.fromisoformat(start_time_str),
                                'end_time': time.fromisoformat(end_time_str),
                                'price': float(price)
                            })
                        except (ValueError, IndexError):
                            continue
                
                # Create time slots for each date
                created_count = 0
                current_date = start_date
                while current_date <= end_date:
                    for slot_data in time_slots:
                        # Check if slot already exists
                        if not TimeSlot.objects.filter(
                            ground=ground,
                            date=current_date,
                            start_time=slot_data['start_time']
                        ).exists():
                            TimeSlot.objects.create(
                                ground=ground,
                                date=current_date,
                                start_time=slot_data['start_time'],
                                end_time=slot_data['end_time'],
                                price=slot_data['price'],
                                is_available=True
                            )
                            created_count += 1
                    current_date += timedelta(days=1)
                
                self.message_user(request, f'Successfully created {created_count} time slots.')
                return HttpResponseRedirect('..')
        else:
            form = BulkTimeSlotForm()
        
        context = {
            'form': form,
            'title': 'Bulk Create Time Slots',
            'opts': self.model._meta,
        }
        return render(request, 'admin/bulk_create_timeslots.html', context)


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'challenger_runs', 'opponent_runs', 'total_overs', 'created_by', 'created_at')
    list_filter = ('created_at', 'challenge__status', 'challenge__challenge_type')
    search_fields = ('challenge__challenger__username', 'challenge__opponent__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Challenge Information', {
            'fields': ('challenge',)
        }),
        ('Challenger Statistics', {
            'fields': ('challenger_runs', 'challenger_wickets', 'challenger_sixes', 'challenger_fours', 'challenger_dots')
        }),
        ('Opponent Statistics', {
            'fields': ('opponent_runs', 'opponent_wickets', 'opponent_sixes', 'opponent_fours', 'opponent_dots')
        }),
        ('Match Details', {
            'fields': ('total_overs', 'match_duration', 'weather_conditions', 'pitch_conditions', 'notes')
        }),
        ('Admin Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin display"""
        return super().get_queryset(request).select_related('challenge', 'challenge__challenger', 'challenge__opponent', 'created_by')
