from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q, F
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class MatchStatistics(models.Model):
    """Comprehensive match statistics for admin analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_stats')
    match = models.ForeignKey('matches.Challenge', on_delete=models.CASCADE, related_name='statistics')
    
    # Batting Statistics
    runs_scored = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    strike_rate = models.FloatField(default=0.0)
    batting_average = models.FloatField(default=0.0)
    
    # Bowling Statistics
    overs_bowled = models.FloatField(default=0.0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets_taken = models.PositiveIntegerField(default=0)
    maidens = models.PositiveIntegerField(default=0)
    bowling_average = models.FloatField(default=0.0)
    economy_rate = models.FloatField(default=0.0)
    bowling_strike_rate = models.FloatField(default=0.0)
    
    # Fielding Statistics
    catches = models.PositiveIntegerField(default=0)
    stumpings = models.PositiveIntegerField(default=0)
    run_outs = models.PositiveIntegerField(default=0)
    
    # Match Context
    match_date = models.DateTimeField()
    ground = models.ForeignKey('grounds.Ground', on_delete=models.SET_NULL, null=True, blank=True)
    opponent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='opponent_stats')
    result = models.CharField(max_length=10, choices=[
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('DRAW', 'Draw'),
        ('TIE', 'Tie')
    ])
    
    # Performance Metrics
    performance_rating = models.FloatField(default=0.0)
    contribution_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_date']
        verbose_name = 'Match Statistics'
        verbose_name_plural = 'Match Statistics'
    
    def __str__(self):
        return f"{self.user.username} - {self.match_date.strftime('%Y-%m-%d')}"
    
    def calculate_batting_average(self):
        """Calculate batting average"""
        if self.balls_faced > 0:
            return round(self.runs_scored / self.balls_faced, 2)
        return 0.0
    
    def calculate_strike_rate(self):
        """Calculate strike rate"""
        if self.balls_faced > 0:
            return round((self.runs_scored / self.balls_faced) * 100, 2)
        return 0.0
    
    def calculate_bowling_average(self):
        """Calculate bowling average"""
        if self.wickets_taken > 0:
            return round(self.runs_conceded / self.wickets_taken, 2)
        return 0.0
    
    def calculate_economy_rate(self):
        """Calculate economy rate"""
        if self.overs_bowled > 0:
            return round(self.runs_conceded / self.overs_bowled, 2)
        return 0.0


class PlayerStatistics(models.Model):
    """Aggregated player statistics for admin analysis"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_stats')
    
    # Career Summary
    total_matches = models.PositiveIntegerField(default=0)
    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    total_catches = models.PositiveIntegerField(default=0)
    total_stumpings = models.PositiveIntegerField(default=0)
    total_run_outs = models.PositiveIntegerField(default=0)
    
    # Batting Career Stats
    career_batting_average = models.FloatField(default=0.0)
    career_strike_rate = models.FloatField(default=0.0)
    highest_score = models.PositiveIntegerField(default=0)
    total_fours = models.PositiveIntegerField(default=0)
    total_sixes = models.PositiveIntegerField(default=0)
    total_balls_faced = models.PositiveIntegerField(default=0)
    
    # Bowling Career Stats
    career_bowling_average = models.FloatField(default=0.0)
    career_economy_rate = models.FloatField(default=0.0)
    career_bowling_strike_rate = models.FloatField(default=0.0)
    best_bowling_figures = models.CharField(max_length=20, blank=True)
    total_overs_bowled = models.FloatField(default=0.0)
    total_runs_conceded = models.PositiveIntegerField(default=0)
    total_maidens = models.PositiveIntegerField(default=0)
    
    # Performance Metrics
    win_percentage = models.FloatField(default=0.0)
    contribution_rating = models.FloatField(default=0.0)
    consistency_rating = models.FloatField(default=0.0)
    
    # Recent Form (Last 10 matches)
    recent_form_rating = models.FloatField(default=0.0)
    recent_batting_average = models.FloatField(default=0.0)
    recent_bowling_average = models.FloatField(default=0.0)
    
    # Rankings
    batting_rank = models.PositiveIntegerField(default=0)
    bowling_rank = models.PositiveIntegerField(default=0)
    all_rounder_rank = models.PositiveIntegerField(default=0)
    overall_rank = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_rank']
        verbose_name = 'Player Statistics'
        verbose_name_plural = 'Player Statistics'
    
    def __str__(self):
        return f"{self.user.username} - Admin Stats"
    
    def update_statistics(self):
        """Update all player statistics"""
        # Get all match statistics for this player
        match_stats = MatchStatistics.objects.filter(user=self.user)
        
        if not match_stats.exists():
            return
        
        # Update career totals
        self.total_matches = match_stats.count()
        self.total_runs = match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
        self.total_wickets = match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
        self.total_catches = match_stats.aggregate(Sum('catches'))['catches__sum'] or 0
        self.total_stumpings = match_stats.aggregate(Sum('stumpings'))['stumpings__sum'] or 0
        self.total_run_outs = match_stats.aggregate(Sum('run_outs'))['run_outs__sum'] or 0
        
        # Calculate batting averages
        total_balls = match_stats.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0
        if total_balls > 0:
            self.career_batting_average = round(self.total_runs / total_balls, 2)
            self.career_strike_rate = round((self.total_runs / total_balls) * 100, 2)
        
        # Calculate bowling averages
        total_overs = match_stats.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
        total_runs_conceded = match_stats.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] or 0
        
        if self.total_wickets > 0:
            self.career_bowling_average = round(total_runs_conceded / self.total_wickets, 2)
        
        if total_overs > 0:
            self.career_economy_rate = round(total_runs_conceded / total_overs, 2)
        
        # Calculate win percentage
        won_matches = match_stats.filter(result='WON').count()
        if self.total_matches > 0:
            self.win_percentage = round((won_matches / self.total_matches) * 100, 2)
        
        # Update recent form (last 10 matches)
        recent_matches = match_stats.order_by('-match_date')[:10]
        if recent_matches.exists():
            recent_runs = recent_matches.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
            recent_balls = recent_matches.aggregate(Sum('balls_faced'))['balls_faced__sum'] or 0
            recent_wickets = recent_matches.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
            recent_overs = recent_matches.aggregate(Sum('overs_bowled'))['overs_bowled__sum'] or 0
            recent_runs_conceded = recent_matches.aggregate(Sum('runs_conceded'))['runs_conceded__sum'] or 0
            
            if recent_balls > 0:
                self.recent_batting_average = round(recent_runs / recent_balls, 2)
            
            if recent_wickets > 0:
                self.recent_bowling_average = round(recent_runs_conceded / recent_wickets, 2)
        
        self.save()


class GroundStatistics(models.Model):
    """Statistics for each ground"""
    ground = models.OneToOneField('grounds.Ground', on_delete=models.CASCADE, related_name='admin_stats')
    
    total_matches = models.PositiveIntegerField(default=0)
    total_runs_scored = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    highest_score = models.PositiveIntegerField(default=0)
    lowest_score = models.PositiveIntegerField(default=0)
    
    # Ground-specific metrics
    batting_friendly_rating = models.FloatField(default=0.0)
    bowling_friendly_rating = models.FloatField(default=0.0)
    overall_rating = models.FloatField(default=0.0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ground Statistics'
        verbose_name_plural = 'Ground Statistics'
    
    def __str__(self):
        return f"{self.ground.name} - Statistics"


class SeasonStatistics(models.Model):
    """Season-wise statistics"""
    season_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    
    total_matches = models.PositiveIntegerField(default=0)
    total_players = models.PositiveIntegerField(default=0)
    total_runs = models.PositiveIntegerField(default=0)
    total_wickets = models.PositiveIntegerField(default=0)
    
    # Season records
    highest_individual_score = models.PositiveIntegerField(default=0)
    best_bowling_figures = models.CharField(max_length=20, blank=True)
    most_runs = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='season_most_runs')
    most_wickets = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='season_most_wickets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Season Statistics'
        verbose_name_plural = 'Season Statistics'
    
    def __str__(self):
        return f"{self.season_name} - Statistics"
