from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Sum, Count, Q, F, Max, Min
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import MatchStatistics, PlayerStatistics, GroundStatistics, SeasonStatistics
from tampere_cricket.accounts.models import User, Profile
from tampere_cricket.matches.models import Challenge
from tampere_cricket.grounds.models import Ground


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with overview statistics"""
    
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    ground_id = request.GET.get('ground', '')
    player_id = request.GET.get('player', '')
    
    # Base querysets
    match_stats = MatchStatistics.objects.all()
    players = User.active_objects()
    grounds = Ground.objects.all()
    
    # Apply filters
    if date_from:
        match_stats = match_stats.filter(match_date__gte=date_from)
    if date_to:
        match_stats = match_stats.filter(match_date__lte=date_to)
    if ground_id:
        match_stats = match_stats.filter(ground_id=ground_id)
    if player_id:
        match_stats = match_stats.filter(user_id=player_id)
    
    # Calculate overview statistics
    total_matches = match_stats.count()
    total_players = players.count()
    total_runs = match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
    total_wickets = match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
    
    # Top performers
    top_batsmen = match_stats.values('user__username', 'user__id').annotate(
        total_runs=Sum('runs_scored'),
        matches=Count('id')
    ).order_by('-total_runs')[:5]
    
    top_bowlers = match_stats.values('user__username', 'user__id').annotate(
        total_wickets=Sum('wickets_taken'),
        matches=Count('id')
    ).order_by('-total_wickets')[:5]
    
    # Recent matches
    recent_matches = match_stats.order_by('-match_date')[:10]
    
    # Ground statistics
    ground_stats = GroundStatistics.objects.all()
    
    context = {
        'total_matches': total_matches,
        'total_players': total_players,
        'total_runs': total_runs,
        'total_wickets': total_wickets,
        'top_batsmen': top_batsmen,
        'top_bowlers': top_bowlers,
        'recent_matches': recent_matches,
        'ground_stats': ground_stats,
        'players': players,
        'grounds': grounds,
        'date_from': date_from,
        'date_to': date_to,
        'selected_ground': ground_id,
        'selected_player': player_id,
    }
    
    return render(request, 'admin_stats/dashboard.html', context)


@staff_member_required
def player_analysis(request, player_id):
    """Detailed player analysis page"""
    player = get_object_or_404(User, id=player_id)
    
    # Get player statistics
    try:
        player_stats = PlayerStatistics.objects.get(user=player)
    except PlayerStatistics.DoesNotExist:
        player_stats = None
    
    # Get match statistics for this player
    match_stats = MatchStatistics.objects.filter(user=player).order_by('-match_date')
    
    # Apply filters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    ground_id = request.GET.get('ground', '')
    
    if date_from:
        match_stats = match_stats.filter(match_date__gte=date_from)
    if date_to:
        match_stats = match_stats.filter(match_date__lte=date_to)
    if ground_id:
        match_stats = match_stats.filter(ground_id=ground_id)
    
    # Calculate performance metrics
    total_matches = match_stats.count()
    total_runs = match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
    total_wickets = match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
    total_balls = match_stats.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0
    total_overs = match_stats.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
    
    # Calculate averages
    batting_average = round(total_runs / total_balls, 2) if total_balls > 0 else 0
    bowling_average = round(match_stats.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] / total_wickets, 2) if total_wickets > 0 else 0
    
    # Performance by ground
    ground_performance = match_stats.values('ground__name').annotate(
        matches=Count('id'),
        runs=Sum('runs_scored'),
        wickets=Sum('wickets_taken'),
        avg_runs=Avg('runs_scored'),
        avg_wickets=Avg('wickets_taken')
    ).order_by('-matches')
    
    # Performance over time (last 10 matches)
    recent_performance = match_stats[:10]
    
    # Opponent analysis
    opponent_analysis = match_stats.values('opponent__username').annotate(
        matches=Count('id'),
        runs=Sum('runs_scored'),
        wickets=Sum('wickets_taken'),
        wins=Count('id', filter=Q(result='WON'))
    ).order_by('-matches')
    
    context = {
        'player': player,
        'player_stats': player_stats,
        'match_stats': match_stats,
        'total_matches': total_matches,
        'total_runs': total_runs,
        'total_wickets': total_wickets,
        'batting_average': batting_average,
        'bowling_average': bowling_average,
        'ground_performance': ground_performance,
        'recent_performance': recent_performance,
        'opponent_analysis': opponent_analysis,
        'grounds': Ground.objects.all(),
        'date_from': date_from,
        'date_to': date_to,
        'selected_ground': ground_id,
    }
    
    return render(request, 'admin_stats/player_analysis.html', context)


@staff_member_required
def player_comparison(request):
    """Compare multiple players"""
    player_ids = request.GET.getlist('players')
    comparison_type = request.GET.get('type', 'batting')  # batting, bowling, all_round
    
    players = []
    comparison_data = []
    
    if player_ids:
        players = User.objects.filter(id__in=player_ids)
        
        for player in players:
            match_stats = MatchStatistics.objects.filter(user=player)
            
            if comparison_type == 'batting':
                data = {
                    'player': player,
                    'matches': match_stats.count(),
                    'runs': match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
                    'balls': match_stats.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0,
                    'average': round(match_stats.aggregate(Avg('runs_scored'))['runs_scored__avg'] or 0, 2),
                    'strike_rate': round(match_stats.aggregate(Avg('strike_rate'))['strike_rate__avg'] or 0, 2),
                    'highest': match_stats.aggregate(Max('runs_scored'))['runs_scored__max'] or 0,
                }
            elif comparison_type == 'bowling':
                data = {
                    'player': player,
                    'matches': match_stats.count(),
                    'wickets': match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0,
                    'overs': match_stats.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0,
                    'average': round(match_stats.aggregate(Avg('bowling_average'))['bowling_average__avg'] or 0, 2),
                    'economy': round(match_stats.aggregate(Avg('economy_rate'))['economy_rate__avg'] or 0, 2),
                    'best': match_stats.aggregate(Max('wickets_taken'))['wickets_taken__max'] or 0,
                }
            else:  # all_round
                data = {
                    'player': player,
                    'matches': match_stats.count(),
                    'runs': match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0,
                    'wickets': match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0,
                    'batting_avg': round(match_stats.aggregate(Avg('runs_scored'))['runs_scored__avg'] or 0, 2),
                    'bowling_avg': round(match_stats.aggregate(Avg('bowling_average'))['bowling_average__avg'] or 0, 2),
                }
            
            comparison_data.append(data)
    
    # Get all players for selection
    all_players = User.active_objects().order_by('username')
    
    context = {
        'players': players,
        'comparison_data': comparison_data,
        'all_players': all_players,
        'comparison_type': comparison_type,
        'selected_players': player_ids,
    }
    
    return render(request, 'admin_stats/player_comparison.html', context)


@staff_member_required
def ground_analysis(request, ground_id):
    """Detailed ground analysis"""
    ground = get_object_or_404(Ground, id=ground_id)
    
    # Get ground statistics
    try:
        ground_stats = GroundStatistics.objects.get(ground=ground)
    except GroundStatistics.DoesNotExist:
        ground_stats = None
    
    # Get match statistics for this ground
    match_stats = MatchStatistics.objects.filter(ground=ground).order_by('-match_date')
    
    # Calculate ground metrics
    total_matches = match_stats.count()
    total_runs = match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
    total_wickets = match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
    average_score = round(total_runs / total_matches, 2) if total_matches > 0 else 0
    
    # Top performers at this ground
    top_batsmen = match_stats.values('user__username').annotate(
        runs=Sum('runs_scored'),
        matches=Count('id'),
        average=Avg('runs_scored')
    ).order_by('-runs')[:5]
    
    top_bowlers = match_stats.values('user__username').annotate(
        wickets=Sum('wickets_taken'),
        matches=Count('id'),
        average=Avg('wickets_taken')
    ).order_by('-wickets')[:5]
    
    # Performance trends over time
    monthly_stats = match_stats.extra(
        select={'month': 'EXTRACT(month FROM match_date)'}
    ).values('month').annotate(
        matches=Count('id'),
        runs=Sum('runs_scored'),
        wickets=Sum('wickets_taken')
    ).order_by('month')
    
    context = {
        'ground': ground,
        'ground_stats': ground_stats,
        'total_matches': total_matches,
        'total_runs': total_runs,
        'total_wickets': total_wickets,
        'average_score': average_score,
        'top_batsmen': top_batsmen,
        'top_bowlers': top_bowlers,
        'monthly_stats': monthly_stats,
        'match_stats': match_stats[:20],  # Recent matches
    }
    
    return render(request, 'admin_stats/ground_analysis.html', context)


@staff_member_required
def records(request):
    """Cricket records and achievements"""
    
    # Individual records
    highest_score = MatchStatistics.objects.aggregate(Max('runs_scored'))['runs_scored__max'] or 0
    best_bowling = MatchStatistics.objects.aggregate(Max('wickets_taken'))['wickets_taken__max'] or 0
    
    # Get record holders
    highest_score_holder = MatchStatistics.objects.filter(runs_scored=highest_score).first()
    best_bowling_holder = MatchStatistics.objects.filter(wickets_taken=best_bowling).first()
    
    # Career records
    career_records = PlayerStatistics.objects.all().order_by('-total_runs')[:10]
    bowling_records = PlayerStatistics.objects.all().order_by('-total_wickets')[:10]
    
    # Ground records
    ground_records = GroundStatistics.objects.all().order_by('-total_matches')[:10]
    
    context = {
        'highest_score': highest_score,
        'highest_score_holder': highest_score_holder,
        'best_bowling': best_bowling,
        'best_bowling_holder': best_bowling_holder,
        'career_records': career_records,
        'bowling_records': bowling_records,
        'ground_records': ground_records,
    }
    
    return render(request, 'admin_stats/records.html', context)


@staff_member_required
def statistics_api(request):
    """API endpoint for statistics data (for charts)"""
    chart_type = request.GET.get('type', 'overview')
    
    if chart_type == 'overview':
        # Monthly match statistics
        data = MatchStatistics.objects.extra(
            select={'month': 'EXTRACT(month FROM match_date)'}
        ).values('month').annotate(
            matches=Count('id'),
            runs=Sum('runs_scored'),
            wickets=Sum('wickets_taken')
        ).order_by('month')
        
        return JsonResponse({
            'labels': [f"Month {item['month']}" for item in data],
            'matches': [item['matches'] for item in data],
            'runs': [item['runs'] or 0 for item in data],
            'wickets': [item['wickets'] or 0 for item in data],
        })
    
    elif chart_type == 'player_performance':
        player_id = request.GET.get('player_id')
        if player_id:
            data = MatchStatistics.objects.filter(user_id=player_id).order_by('match_date')
            return JsonResponse({
                'labels': [match.match_date.strftime('%Y-%m-%d') for match in data],
                'runs': [match.runs_scored for match in data],
                'wickets': [match.wickets_taken for match in data],
            })
    
    return JsonResponse({'error': 'Invalid chart type'})
