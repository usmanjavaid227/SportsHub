from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import User, Profile
from .forms import RegistrationForm, CustomAuthenticationForm, ProfileEditForm


def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        privacy_policy = request.POST.get('privacy_policy')
        
        if not privacy_policy:
            messages.error(request, 'You must agree to the Privacy Policy and Terms of Service to create an account.')
            return render(request, 'auth/register.html', {'form': form})
        
        if form.is_valid():
            user = form.save()
            # Auto-create Profile for new user with default values
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'ranking_change_batting': 0,
                    'ranking_change_bowling': 0,
                    'ranking_change_overall': 0,
                    'previous_batting_rank': 0,
                    'previous_bowling_rank': 0,
                    'previous_overall_rank': 0
                }
            )
            login(request, user)
            messages.success(request, f'Welcome to SportsHub, {user.username}!')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def custom_login(request):
    """Custom login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


@login_required
def profile(request):
    """User profile view"""
    # Get or create profile for the user
    from tampere_cricket.accounts.models import Profile
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Update statistics based on completed matches
    stats = profile.update_statistics()
    
    # Get recent matches for the user
    recent_matches = profile.get_recent_matches(limit=10)
    
    # Get user's current rank
    user_rank = profile.get_rank()
    
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile,
        'recent_matches': recent_matches,
        'user_rank': user_rank
    })


def public_profile_view(request, user_id):
    """Public profile view for other users - shows limited information"""
    user = get_object_or_404(User, id=user_id)
    
    # Check if user is viewing their own profile
    is_own_profile = request.user.is_authenticated and request.user.id == user.id
    
    # Get or create profile for the user
    from tampere_cricket.accounts.models import Profile
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
    
    # Update statistics based on completed matches
    stats = profile.update_statistics()
    
    # Get additional data for charts and trends
    recent_matches = profile.get_recent_matches(limit=10)
    performance_trend = profile.get_performance_trend(days=30)
    
    # Calculate averages
    avg_runs_per_match = profile.runs / profile.matches_played if profile.matches_played > 0 else 0
    avg_wickets_per_match = profile.wickets / profile.matches_played if profile.matches_played > 0 else 0
    
    # Prepare chart data
    chart_data = {
        'win_loss': {
            'labels': ['Wins', 'Losses'],
            'data': [profile.wins, profile.losses],
            'colors': ['#28a745', '#dc3545']
        },
        'performance': {
            'labels': ['Runs', 'Wickets', 'Batting Rating', 'Bowling Rating'],
            'data': [profile.runs, profile.wickets, int(profile.batting_rating), int(profile.bowling_rating)],
            'colors': ['#007bff', '#dc3545', '#ffc107', '#28a745']
        },
        'trend': {
            'labels': [str(item['date']) for item in performance_trend],
            'data': [item['win_rate'] for item in performance_trend]
        }
    }
    
    # Get user's current rank
    user_rank = profile.get_rank()
    
    return render(request, 'profiles/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'stats': stats,
        'recent_matches': recent_matches,
        'performance_trend': performance_trend,
        'chart_data': chart_data,
        'avg_runs_per_match': avg_runs_per_match,
        'avg_wickets_per_match': avg_wickets_per_match,
        'is_own_profile': is_own_profile,  # Pass flag to template
        'user_rank': user_rank
    })


@login_required
def profile_edit(request):
    """Profile edit view"""
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


def custom_logout(request):
    """Custom logout view that redirects to home page"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been successfully logged out.")
    return redirect('home')
