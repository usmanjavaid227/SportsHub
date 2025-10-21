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
    for user in User.active_objects():
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
    
    # Get top 3 highlights items (not older than 1 month)
    from tampere_cricket.news.models import News
    from django.utils import timezone
    from datetime import timedelta
    
    one_month_ago = timezone.now() - timedelta(days=30)
    recent_news = News.objects.filter(
        published=True,
        created_at__gte=one_month_ago
    ).order_by('-created_at')[:3]
    
    # Calculate real statistics for About section
    total_players = User.objects.count()
    total_challenges = Challenge.objects.count()
    total_grounds = Ground.objects.filter(is_available=True).count()
    
    # Check if profile is incomplete (for popup display)
    is_profile_incomplete = False
    if request.user.is_authenticated:
        required_fields = ['first_name', 'last_name', 'email', 'phone']
        for field in required_fields:
            value = getattr(request.user, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                is_profile_incomplete = True
                break
    
    context = {
        'recent_challenges': recent_challenges,
        'players': players,
        'top_grounds': top_grounds,
        'recent_news': recent_news,
        'total_players': total_players,
        'total_challenges': total_challenges,
        'total_grounds': total_grounds,
        'is_profile_incomplete': is_profile_incomplete,
    }
    return render(request, 'home.html', context)


def leaderboard(request):
    """Leaderboard page view with pagination and search"""
    from django.db.models import Count, Q, F
    from django.core.paginator import Paginator
    from tampere_cricket.accounts.models import Profile
    
    # Get search query and page number
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)
    players_per_page = 20
    
    # Get all active users with their profile statistics
    all_players = []
    for user in User.active_objects():
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
                all_players.append(player)
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
                all_players.append(player)
    
    # Apply search filter if provided
    if search_query:
        all_players = [player for player in all_players if search_query.lower() in player.username.lower()]
    
    # Sort by rating (descending), then by total_matches (descending), then by total_wins (descending)
    all_players = sorted(all_players, key=lambda x: (x.rating, x.total_matches, x.total_wins), reverse=True)
    
    # Create paginator
    paginator = Paginator(all_players, players_per_page)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'players': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'leaderboard.html', context)




def delete_profile(request):
    """Soft delete user profile"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        request.user.soft_delete(reason)
        messages.success(request, 'Your profile has been deleted successfully.')
        return redirect('home')
    
    return render(request, 'delete_profile.html')


def news(request):
    """Highlights page view"""
    return render(request, 'highlights.html')


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
        challenge_rules = request.POST.get('challenge_rules')
        
        if not challenge_rules:
            messages.error(request, 'You must agree to the Challenge Rules & Guidelines to create a challenge.')
            return render(request, 'challenges/create.html', {"form": form})
        
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


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'terms_of_service.html')


def challenge_rules(request):
    """Challenge Rules page"""
    return render(request, 'challenge_rules.html')
