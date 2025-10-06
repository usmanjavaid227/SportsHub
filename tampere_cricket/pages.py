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
    
    # Get top 3 players for leaderboard preview using Profile statistics
    from tampere_cricket.accounts.models import Profile
    
    all_players = []
    for user in User.objects.all():
        try:
            profile = Profile.objects.get(user=user)
            stats = profile.update_statistics()
            
            player = user
            player.total_matches = profile.matches_played
            player.total_wins = profile.wins
            player.total_losses = profile.losses
            player.win_rate = profile.get_win_rate()
            player.rating = profile.rating
            
            if player.total_matches > 0:
                all_players.append(player)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            stats = profile.update_statistics()
            
            player = user
            player.total_matches = profile.matches_played
            player.total_wins = profile.wins
            player.total_losses = profile.losses
            player.win_rate = profile.get_win_rate()
            player.rating = profile.rating
            
            if player.total_matches > 0:
                all_players.append(player)
    
    # Sort and get top 3
    players = sorted(all_players, key=lambda x: (x.rating, x.total_matches, x.total_wins), reverse=True)[:3]
    
    # Get top 3 grounds
    from tampere_cricket.grounds.models import Ground
    top_grounds = Ground.objects.filter(is_available=True)[:3]
    
    # Get top 3 news items
    from tampere_cricket.news.models import News
    recent_news = News.objects.filter(published=True).order_by('-created_at')[:3]
    
    # Calculate real statistics for About section
    total_players = User.objects.count()
    total_challenges = Challenge.objects.count()
    total_grounds = Ground.objects.filter(is_available=True).count()
    
    context = {
        'recent_challenges': recent_challenges,
        'players': players,
        'top_grounds': top_grounds,
        'recent_news': recent_news,
        'total_players': total_players,
        'total_challenges': total_challenges,
        'total_grounds': total_grounds,
    }
    return render(request, 'home.html', context)


def leaderboard(request):
    """Leaderboard page view"""
    from django.db.models import Count, Q, F
    from tampere_cricket.accounts.models import Profile
    
    # Get all users with their profile statistics
    players = []
    for user in User.objects.all():
        try:
            profile = Profile.objects.get(user=user)
            # Update statistics to ensure they're current
            stats = profile.update_statistics()
            
            # Create a player object with the correct statistics
            player = user
            player.total_matches = profile.matches_played
            player.total_wins = profile.wins
            player.total_losses = profile.losses
            player.win_rate = profile.get_win_rate()
            player.rating = profile.rating
            
            # Only include players with matches
            if player.total_matches > 0:
                players.append(player)
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=user)
            stats = profile.update_statistics()
            
            player = user
            player.total_matches = profile.matches_played
            player.total_wins = profile.wins
            player.total_losses = profile.losses
            player.win_rate = profile.get_win_rate()
            player.rating = profile.rating
            
            if player.total_matches > 0:
                players.append(player)
    
    # Sort by rating (descending), then by total_matches (descending), then by total_wins (descending)
    players = sorted(players, key=lambda x: (x.rating, x.total_matches, x.total_wins), reverse=True)
    
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
