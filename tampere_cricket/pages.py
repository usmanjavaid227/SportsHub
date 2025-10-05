from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tampere_cricket.matches.models import Challenge, TimeSlot
from tampere_cricket.accounts.models import User
from tampere_cricket.grounds.models import Ground
from tampere_cricket.news.models import News


def home(request):
    """Home page view"""
    from django.db.models import Count, Q
    
    # Get top 3 recent challenges
    recent_challenges = Challenge.objects.filter(status__in=['OPEN', 'PENDING', 'ACCEPTED']).order_by('-created_at')[:3]
    
    # Get top 3 players for leaderboard preview
    players = User.objects.annotate(
        total_matches=Count('challenges_made', filter=Q(challenges_made__status='COMPLETED')) + 
                     Count('challenges_received', filter=Q(challenges_received__status='COMPLETED')),
        total_wins=Count('challenges_won')
    ).filter(total_matches__gt=0).order_by('-total_wins')[:3]
    
    # Calculate ratings for top 3 players
    for player in players:
        if player.total_matches > 0:
            win_rate = (player.total_wins / player.total_matches) * 100
            player.rating = win_rate + (player.total_matches * 10)
            player.win_rate = round(win_rate, 1)
        else:
            player.rating = 0
            player.win_rate = 0
    
    # Get top 3 grounds
    from tampere_cricket.grounds.models import Ground
    top_grounds = Ground.objects.filter(is_available=True)[:3]
    
    # Get top 3 news items
    from tampere_cricket.news.models import News
    recent_news = News.objects.filter(published=True).order_by('-created_at')[:3]
    
    context = {
        'recent_challenges': recent_challenges,
        'players': players,
        'top_grounds': top_grounds,
        'recent_news': recent_news,
    }
    return render(request, 'home.html', context)


def leaderboard(request):
    """Leaderboard page view"""
    from django.db.models import Count, Q, F
    
    # Get all users with their statistics
    players = User.objects.annotate(
        total_matches=Count('challenges_made', filter=Q(challenges_made__status='COMPLETED')) + 
                     Count('challenges_received', filter=Q(challenges_received__status='COMPLETED')),
        total_wins=Count('challenges_won'),
        total_losses=Count('challenges_made', filter=Q(challenges_made__status='COMPLETED', challenges_made__winner__isnull=False)) + 
                    Count('challenges_received', filter=Q(challenges_received__status='COMPLETED', challenges_received__winner__isnull=False)) - 
                    Count('challenges_won')
    ).filter(total_matches__gt=0).order_by('-total_wins', '-total_matches')
    
    # Calculate ratings and win rates for each player
    for player in players:
        if player.total_matches > 0:
            win_rate = (player.total_wins / player.total_matches) * 100
            player.rating = win_rate + (player.total_matches * 10)  # Bonus for more matches
            player.win_rate = round(win_rate, 1)
        else:
            player.rating = 0
            player.win_rate = 0
    
    # Re-sort by rating
    players = sorted(players, key=lambda x: x.rating, reverse=True)
    
    context = {
        'players': players,
    }
    return render(request, 'leaderboard.html', context)


def grounds(request):
    """Grounds page view"""
    return render(request, 'grounds.html')


def news(request):
    """News page view"""
    return render(request, 'news.html')


def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'profile.html')


@login_required
def profile_edit_view(request):
    """Profile edit view"""
    from accounts.forms import ProfileEditForm
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})


def challenge_create_view(request):
    """Challenge creation view with profile validation"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to create a challenge.")
        return redirect('login')

    # Check if profile is complete
    from accounts.forms import ProfileCompletionForm
    profile_form = ProfileCompletionForm(instance=request.user)
    if not profile_form.is_profile_complete():
        messages.warning(request, "Please complete your profile before creating a challenge.")
        return redirect('profile_edit')

    # Prevent creating more than one active challenge at a time (OPEN/PENDING/ACCEPTED)
    from matches.views import has_active_challenge, get_active_challenge
    if has_active_challenge(request.user):
        active_challenge = get_active_challenge(request.user)
        messages.warning(
            request, 
            f'You already have an active challenge. Please complete or cancel your current challenge before creating a new one. '
            f'Current challenge: {active_challenge.challenge_type} vs {active_challenge.opponent.username if active_challenge.opponent else "Open to All"}'
        )
        return redirect('challenge_detail', challenge_id=active_challenge.id)

    if request.method == 'POST':
        from matches.forms import ChallengeForm
        form = ChallengeForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                challenge = form.save(commit=False)
                challenge.challenger = request.user
                challenge.save()
                messages.success(request, "Challenge created.")
                return redirect('challenge_detail', challenge_id=challenge.id)
            except forms.ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        from matches.forms import ChallengeForm
        form = ChallengeForm(user=request.user)

    return render(request, 'challenges/create.html', {"form": form})
