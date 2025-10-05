from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Challenge, TimeSlot, MatchResult
from .serializers import ChallengeSerializer
from .forms import ChallengeForm, MatchResultForm
from django.contrib.auth import get_user_model

User = get_user_model()


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        challenge = self.get_object()
        if challenge.status == 'OPEN':
            challenge.opponent = request.user
            challenge.status = 'ACCEPTED'
            challenge.save()
            return Response({'status': 'Challenge accepted'})
        return Response({'error': 'Challenge cannot be accepted'}, status=400)


# Traditional Django views for templates
def challenges_list(request):
    """List all challenges with optional status filtering"""
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    challenges = Challenge.objects.all().order_by('-created_at')
    
    # Apply status filter
    if status_filter == 'open':
        challenges = challenges.filter(status='OPEN')
    elif status_filter == 'accepted':
        challenges = challenges.filter(status='ACCEPTED')
    elif status_filter == 'completed':
        challenges = challenges.filter(status='COMPLETED')
    elif status_filter == 'pending':
        challenges = challenges.filter(status='PENDING')
    elif status_filter == 'cancelled':
        challenges = challenges.filter(status='CANCELLED')
    
    # Get counts for each status
    status_counts = {
        'all': Challenge.objects.count(),
        'open': Challenge.objects.filter(status='OPEN').count(),
        'accepted': Challenge.objects.filter(status='ACCEPTED').count(),
        'completed': Challenge.objects.filter(status='COMPLETED').count(),
        'pending': Challenge.objects.filter(status='PENDING').count(),
        'cancelled': Challenge.objects.filter(status='CANCELLED').count(),
    }
    
    # Check if user profile is complete (for authenticated users)
    profile_complete = True
    missing_field = None
    if request.user.is_authenticated:
        profile_complete, missing_field = is_profile_complete(request.user)
    
    context = {
        'challenges': challenges,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'profile_complete': profile_complete,
        'missing_field': missing_field,
    }
    return render(request, 'challenges/list.html', context)


def challenge_detail(request, challenge_id):
    """Display challenge details"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    return render(request, 'challenges/detail.html', {'challenge': challenge})


@login_required
def challenge_edit(request, challenge_id):
    """Edit a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Only the creator can edit
    if request.user != challenge.challenger:
        messages.error(request, "You can only edit your own challenges")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # Only allow editing if challenge is PENDING or OPEN (not yet accepted by opponent)
    if challenge.status not in ['PENDING', 'OPEN']:
        if challenge.status == 'ACCEPTED':
            messages.error(request, "Cannot edit challenge that has been accepted by the opponent")
        elif challenge.status == 'COMPLETED':
            messages.error(request, "Cannot edit challenge that has been completed")
        else:
            messages.error(request, "Cannot edit challenge in its current status")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    if request.method == 'POST':
        form = ChallengeForm(request.POST, user=request.user, instance=challenge)
        if form.is_valid():
            # Update challenge with form data
            updated_challenge = form.save(commit=False)
            updated_challenge.challenger = request.user  # Ensure challenger is set
            updated_challenge.save()
            
            messages.success(request, "Challenge updated successfully")
            return redirect('challenge_detail', challenge_id=challenge_id)
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = ChallengeForm(user=request.user, instance=challenge)
    
    return render(request, 'challenges/edit.html', {'form': form, 'challenge': challenge})


@login_required
def challenge_delete(request, challenge_id):
    """Delete a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Only the creator can delete
    if request.user != challenge.challenger:
        return HttpResponseForbidden("You can only delete your own challenges")
    
    # Only allow deleting if challenge is OPEN or PENDING
    if challenge.status not in ['OPEN', 'PENDING']:
        messages.error(request, "Cannot delete challenge that has been accepted or completed")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    if request.method == 'POST':
        challenge.delete()
        messages.success(request, "Challenge deleted successfully")
        return redirect('challenges_list')
    
    return render(request, 'challenges/delete_confirm.html', {'challenge': challenge})


@login_required
def challenge_accept(request, challenge_id):
    """Accept a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if user can accept this challenge
    if challenge.challenger == request.user:
        messages.error(request, "You cannot accept your own challenge")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # For PENDING challenges, only the specific opponent can accept
    if challenge.status == 'PENDING':
        if challenge.opponent != request.user:
            messages.error(request, "This challenge was sent to a specific player. Only they can accept it.")
            return redirect('challenge_detail', challenge_id=challenge_id)
    elif challenge.status != 'OPEN':
        messages.error(request, "This challenge is not available for acceptance")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    if request.method == 'POST':
        challenge.opponent = request.user
        challenge.status = 'ACCEPTED'
        challenge.accepted_at = timezone.now()
        challenge.save()
        messages.success(request, "Challenge accepted successfully!")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    return render(request, 'challenges/accept_confirm.html', {'challenge': challenge})


@login_required
def open_challenge_accept(request, challenge_id):
    """Accept an open challenge (direct POST)"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if user can accept this challenge
    if challenge.challenger == request.user:
        messages.error(request, "You cannot accept your own challenge")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # For PENDING challenges, only the specific opponent can accept
    if challenge.status == 'PENDING':
        if challenge.opponent != request.user:
            messages.error(request, "This challenge was sent to a specific player. Only they can accept it.")
            return redirect('challenge_detail', challenge_id=challenge_id)
    elif challenge.status != 'OPEN':
        messages.error(request, "This challenge is not available for acceptance")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    challenge.opponent = request.user
    challenge.status = 'ACCEPTED'
    challenge.accepted_at = timezone.now()
    challenge.save()
    messages.success(request, "Challenge accepted successfully!")
    return redirect('challenge_detail', challenge_id=challenge_id)


def is_profile_complete(user):
    """Check if user profile is complete for challenge creation"""
    required_fields = [
        'phone', 'bio', 'role', 'experience_level', 
        'preferred_batting_style', 'preferred_bowling_style', 'years_playing'
    ]
    
    for field in required_fields:
        value = getattr(user, field, None)
        if not value or (isinstance(value, str) and value.strip() == ''):
            return False, field
    
    return True, None


def has_active_challenge(user):
    """Check if user has an active challenge"""
    return Challenge.objects.filter(
        challenger=user, 
        status__in=['OPEN', 'PENDING', 'ACCEPTED']
    ).exists()


def get_active_challenge(user):
    """Get user's active challenge if it exists"""
    return Challenge.objects.filter(
        challenger=user, 
        status__in=['OPEN', 'PENDING', 'ACCEPTED']
    ).first()


def challenge_create(request):
    """Create a new challenge - redirects non-authenticated users to login"""
    # Redirect non-authenticated users to login
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to create a challenge.')
        return redirect('login')
    
    # Check if profile is complete
    profile_complete, missing_field = is_profile_complete(request.user)
    
    if not profile_complete:
        messages.warning(
            request, 
            f'Please complete your profile before creating a challenge. Missing: {missing_field.replace("_", " ").title()}'
        )
        return redirect('profile_edit')
    
    # Check for active challenges - prevent creating more than one active challenge at a time
    if has_active_challenge(request.user):
        active_challenge = get_active_challenge(request.user)
        messages.warning(
            request, 
            f'You already have an active challenge. Please complete or cancel your current challenge before creating a new one. '
            f'Current challenge: {active_challenge.challenge_type} vs {active_challenge.opponent.username if active_challenge.opponent else "Open to All"}'
        )
        return redirect('challenge_detail', challenge_id=active_challenge.id)
    
    if request.method == 'POST':
        form = ChallengeForm(request.POST, user=request.user)
        if form.is_valid():
            # Create challenge instance with challenger set
            challenge = form.save(commit=False)
            challenge.challenger = request.user
            challenge.status = 'OPEN'
            challenge.created_at = timezone.now()
            
            # If a specific opponent is selected, set status to PENDING
            # If no opponent (Open to All), set status to OPEN
            if challenge.opponent:
                challenge.status = 'PENDING'
            else:
                challenge.status = 'OPEN'
            
            # Handle time slot - set time from selected time slot
            time_slot_id = request.POST.get('time_slot')
            if time_slot_id:
                try:
                    from tampere_cricket.matches.models import TimeSlot
                    time_slot = TimeSlot.objects.get(id=time_slot_id)
                    challenge.time = time_slot.start_time
                    challenge.ground = time_slot.ground
                except TimeSlot.DoesNotExist:
                    pass
            
            # Set scheduled_at if both date and time are provided
            if challenge.date and challenge.time:
                from datetime import datetime
                scheduled_at = datetime.combine(challenge.date, challenge.time)
                # Make it timezone-aware
                challenge.scheduled_at = timezone.make_aware(scheduled_at)
            
            # Handle summary field - combine with description if provided
            summary = form.cleaned_data.get('summary', '')
            if summary and challenge.description:
                challenge.description = f"{challenge.description}\n\nAdditional Comments: {summary}"
            elif summary:
                challenge.description = f"Additional Comments: {summary}"
            
            # Save the challenge
            try:
                challenge.save()
                if challenge.opponent:
                    messages.success(request, f'Challenge sent to {challenge.opponent.username}! They can now accept or decline.')
                else:
                    messages.success(request, f'Challenge created successfully! Your challenge is now open to all players.')
                return redirect('challenge_detail', challenge_id=challenge.id)
            except Exception as e:
                messages.error(request, f'Error creating challenge: {str(e)}')
                return render(request, 'challenges/create.html', {'form': form})
        else:
            # Form is not valid, show errors
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ChallengeForm(user=request.user)
    
    return render(request, 'challenges/create.html', {'form': form})


@csrf_exempt
@require_http_methods(["GET"])
def timeslots_api(request):
    """API endpoint to get available time slots for a specific date"""
    date = request.GET.get('date')
    
    if not date:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)
    
    try:
        from datetime import datetime
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Get only admin-created time slots for the selected date
    time_slots = TimeSlot.objects.filter(date=selected_date, is_available=True).order_by('start_time')
    
    # Format the response
    slots_data = []
    for slot in time_slots:
        # Count existing challenges for this time slot
        existing_challenges = Challenge.objects.filter(
            scheduled_at__date=selected_date,
            scheduled_at__time__gte=slot.start_time,
            scheduled_at__time__lt=slot.end_time,
            status__in=['OPEN', 'PENDING', 'ACCEPTED']
        ).count()
        
        # Calculate availability status
        max_challenges = 2  # Maximum challenges per time slot
        is_slot_available = existing_challenges < max_challenges
        
        slots_data.append({
            'id': slot.id,
            'display': f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}",
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M'),
            'price': float(slot.price),
            'is_available': is_slot_available,
            'current_count': existing_challenges,
            'max_challenges': max_challenges,
            'ground_name': slot.ground.name,
        })
    
    return JsonResponse({
        'slots': slots_data,
        'date': date,
        'total_slots': len(slots_data),
        'admin_created': True  # Indicate these are admin-created slots
    })


# Admin permission check
def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_update_match_result(request, challenge_id):
    """Admin view to update match results and statistics"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    # Check if challenge is completed or can be updated
    if challenge.status not in ['COMPLETED', 'ACCEPTED']:
        messages.error(request, "Can only update results for completed or accepted challenges.")
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # Get or create match result
    match_result, created = MatchResult.objects.get_or_create(
        challenge=challenge,
        defaults={'created_by': request.user}
    )
    
    if request.method == 'POST':
        form = MatchResultForm(request.POST, instance=match_result, challenge=challenge)
        if form.is_valid():
            match_result = form.save(commit=False)
            match_result.created_by = request.user
            match_result.save()
            
            # Determine winner - manual selection or automatic
            manual_winner_id = form.cleaned_data.get('manual_winner')
            if manual_winner_id:
                # Manual winner selection
                from django.contrib.auth import get_user_model
                User = get_user_model()
                winner = get_object_or_404(User, id=manual_winner_id)
            else:
                # Auto-determine winner based on statistics
                winner = match_result.determine_winner()
            
            challenge.winner = winner
            challenge.status = 'COMPLETED'
            challenge.save()
            
            messages.success(request, f'Match results updated successfully! Winner: {winner.username}')
            return redirect('challenge_detail', challenge_id=challenge_id)
    else:
        form = MatchResultForm(instance=match_result, challenge=challenge)
    
    return render(request, 'challenges/admin_update_result.html', {
        'challenge': challenge,
        'form': form,
        'match_result': match_result
    })


@user_passes_test(is_admin)
def admin_select_winner(request, challenge_id):
    """Admin view to manually select winner"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if request.method == 'POST':
        winner_id = request.POST.get('winner')
        if winner_id:
            winner = get_object_or_404(User, id=winner_id)
            challenge.winner = winner
            challenge.status = 'COMPLETED'
            challenge.save()
            messages.success(request, f'Winner set to {winner.username}')
        else:
            messages.error(request, 'Please select a winner')
        
        return redirect('challenge_detail', challenge_id=challenge_id)
    
    # Get possible winners (challenger and opponent)
    possible_winners = [challenge.challenger]
    if challenge.opponent:
        possible_winners.append(challenge.opponent)
    
    return render(request, 'challenges/admin_select_winner.html', {
        'challenge': challenge,
        'possible_winners': possible_winners
    })
