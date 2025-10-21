from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import User, Profile
from .forms import RegistrationForm, CustomAuthenticationForm, ProfileEditForm, PasswordChangeForm


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
            remember_me = request.POST.get('remember') == '1'
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Handle remember me functionality
                if remember_me:
                    # Set session to expire in 2 weeks
                    request.session.set_expiry(1209600)  # 2 weeks in seconds
                    # Also set the session cookie to persist
                    request.session.modified = True
                    messages.success(request, f'Welcome back, {username}! You will stay logged in for 2 weeks.')
                else:
                    # Use default session expiry (browser session)
                    request.session.set_expiry(0)
                    messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                # Add authentication error to form's non-field errors
                form.add_error(None, 'Invalid username or password.')
        else:
            # Add form validation errors to form's non-field errors
            form.add_error(None, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


def profile(request, user_id=None):
    """Unified profile view - handles both own profile and public profile"""
    from tampere_cricket.accounts.models import Profile
    
    # Determine which user's profile to show
    if user_id:
        # Public profile - viewing another user's profile
        profile_user = get_object_or_404(User, id=user_id)
        is_own_profile = request.user.is_authenticated and request.user.id == user_id
    else:
        # Own profile - user must be logged in
        if not request.user.is_authenticated:
            return redirect('login')
        profile_user = request.user
        is_own_profile = True
    
    # Get or create profile for the user
    try:
        user_profile = Profile.objects.get(user=profile_user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=profile_user)
    
    # Update statistics based on completed matches
    stats = user_profile.update_statistics()
    
    # Get recent matches for the user
    recent_matches = user_profile.get_recent_matches(limit=10)
    
    # Get user's current rank (only if they've played matches)
    user_rank = user_profile.get_rank() if user_profile.matches_played > 0 else None
    
    # Check if profile is incomplete (for popup display)
    is_profile_incomplete = False
    if is_own_profile:
        required_fields = ['first_name', 'last_name', 'email', 'phone']
        for field in required_fields:
            value = getattr(profile_user, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                is_profile_incomplete = True
                break
    
    # Get additional data for charts and trends (only for own profile or if logged in)
    performance_trend = []
    chart_data = {}
    avg_runs_per_match = 0
    avg_wickets_per_match = 0
    
    if request.user.is_authenticated:
        performance_trend = user_profile.get_performance_trend(days=30)
        
        # Calculate averages
        avg_runs_per_match = user_profile.runs / user_profile.matches_played if user_profile.matches_played > 0 else 0
        avg_wickets_per_match = user_profile.wickets / user_profile.matches_played if user_profile.matches_played > 0 else 0
        
        # Prepare chart data
        chart_data = {
            'win_loss': {
                'labels': ['Wins', 'Losses'],
                'data': [user_profile.wins, user_profile.losses],
                'colors': ['#28a745', '#dc3545']
            },
            'performance': {
                'labels': ['Runs', 'Wickets', 'Batting Rating', 'Bowling Rating'],
                'data': [user_profile.runs, user_profile.wickets, int(user_profile.batting_rating), int(user_profile.bowling_rating)],
                'colors': ['#007bff', '#dc3545', '#ffc107', '#28a745']
            },
            'trend': {
                'labels': [str(item['date']) for item in performance_trend],
                'data': [item['win_rate'] for item in performance_trend]
            }
        }
    
    return render(request, 'profile.html', {
        'user': profile_user,
        'profile': user_profile,
        'recent_matches': recent_matches,
        'user_rank': user_rank,
        'is_own_profile': is_own_profile,
        'is_profile_incomplete': is_profile_incomplete,
        'performance_trend': performance_trend,
        'chart_data': chart_data,
        'avg_runs_per_match': avg_runs_per_match,
        'avg_wickets_per_match': avg_wickets_per_match
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


@login_required
def player_stats(request):
    """Player stats page with professional sports-style layout"""
    # Get or create profile for the user
    from tampere_cricket.accounts.models import Profile
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Update statistics based on completed matches
    stats = profile.update_statistics()
    
    # Get user's current rank
    user_rank = profile.get_rank() if profile.matches_played > 0 else None
    
    return render(request, 'player_stats.html', {
        'user': request.user,
        'profile': profile,
        'user_rank': user_rank
    })


@require_http_methods(["POST"])
def check_username(request):
    """Check if username is available"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({'available': False, 'message': 'Username is required'})
        
        # Check if username exists
        exists = User.objects.filter(username__iexact=username).exists()
        
        return JsonResponse({
            'available': not exists,
            'message': 'Username is available' if not exists else 'Username is already taken'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'available': False, 'message': 'Invalid request'})
    except Exception as e:
        return JsonResponse({'available': False, 'message': 'Server error'})


@login_required
def change_password(request):
    """Change user password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})
