from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=24, blank=True, default='')
    city = models.CharField(max_length=100, default='Tampere')
    bio = models.TextField(blank=True, default='', help_text="Tell us about your cricket experience")
    role = models.CharField(
        max_length=10,
        choices=[('batter', 'Batter'), ('bowler', 'Bowler'), ('allrounder', 'All Rounder')],
        default='allrounder',
        help_text="Your primary role in cricket"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('professional', 'Professional')
        ],
        default='intermediate',
        help_text="Your cricket experience level"
    )
    preferred_batting_style = models.CharField(
        max_length=20,
        choices=[
            ('right_handed', 'Right Handed'),
            ('left_handed', 'Left Handed')
        ],
        blank=True,
        help_text="Your batting style"
    )
    preferred_bowling_style = models.CharField(
        max_length=30,
        choices=[
            ('right_arm_fast', 'Right Arm Fast'),
            ('right_arm_medium', 'Right Arm Medium'),
            ('right_arm_spin', 'Right Arm Spin'),
            ('left_arm_fast', 'Left Arm Fast'),
            ('left_arm_medium', 'Left Arm Medium'),
            ('left_arm_spin', 'Left Arm Spin'),
            ('leg_spin', 'Leg Spin'),
            ('off_spin', 'Off Spin')
        ],
        blank=True,
        help_text="Your bowling style"
    )
    years_playing = models.PositiveIntegerField(
        default=0,
        help_text="Years of cricket experience"
    )
    
    # Soft delete fields
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="When the user was soft deleted")
    deleted_reason = models.TextField(blank=True, help_text="Reason for deletion")
    
    def soft_delete(self, reason=""):
        """Soft delete the user instead of hard delete"""
        from django.utils import timezone
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_reason = reason
        self.is_active = False  # Also deactivate the account
        self.save()
        
        # Update username to avoid conflicts if user tries to re-register
        self.username = f"deleted_{self.id}_{self.username}"
        self.email = f"deleted_{self.id}_{self.email}"
        self.save()
    
    def restore(self):
        """Restore a soft-deleted user"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_reason = ""
        self.is_active = True
        self.save()
    
    @classmethod
    def active_objects(cls):
        """Manager for active (non-deleted) users"""
        return cls.objects.filter(is_deleted=False)
    
    @classmethod
    def deleted_objects(cls):
        """Manager for soft-deleted users"""
        return cls.objects.filter(is_deleted=True)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matches_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=1000.0)  # Elo-style rating
    batting_rating = models.FloatField(default=1000.0)
    bowling_rating = models.FloatField(default=1000.0)
    runs = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    balls_bowled = models.PositiveIntegerField(default=0)
    fcm_token = models.CharField(max_length=300, blank=True)
    
    # Ranking fields
    previous_batting_rank = models.PositiveIntegerField(blank=True, default=0, null=True)
    previous_bowling_rank = models.PositiveIntegerField(blank=True, default=0, null=True)
    previous_overall_rank = models.PositiveIntegerField(blank=True, default=0, null=True)
    ranking_change_batting = models.IntegerField(default=0)
    ranking_change_bowling = models.IntegerField(default=0)
    ranking_change_overall = models.IntegerField(default=0)
    
    def update_statistics(self):
        """Update user statistics based on completed challenges"""
        from tampere_cricket.matches.models import Challenge, MatchResult
        
        # Get all completed challenges where user was either challenger or opponent
        completed_challenges = Challenge.objects.filter(
            models.Q(challenger=self.user) | models.Q(opponent=self.user),
            status='COMPLETED'
        )
        
        # Reset counters
        self.matches_played = 0
        self.wins = 0
        self.losses = 0
        self.runs = 0
        self.wickets = 0
        self.balls_faced = 0
        self.balls_bowled = 0
        
        for challenge in completed_challenges:
            self.matches_played += 1
            
            # Check if user won
            if challenge.winner == self.user:
                self.wins += 1
            else:
                self.losses += 1
            
            # Get match result if exists
            try:
                match_result = challenge.match_result
                if challenge.challenger == self.user:
                    # User was challenger
                    self.runs += match_result.challenger_runs
                    self.wickets += match_result.challenger_wickets
                    # Add other stats as needed
                elif challenge.opponent == self.user:
                    # User was opponent
                    self.runs += match_result.opponent_runs
                    self.wickets += match_result.opponent_wickets
            except MatchResult.DoesNotExist:
                pass
        
        # Calculate win rate
        if self.matches_played > 0:
            win_rate = (self.wins / self.matches_played) * 100
        else:
            win_rate = 0
        
        # Update ratings based on performance (simplified Elo system)
        self._update_ratings()
        
        self.save()
        return {
            'matches_played': self.matches_played,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': win_rate,
            'runs': self.runs,
            'wickets': self.wickets,
            'rating': self.rating,
            'batting_rating': self.batting_rating,
            'bowling_rating': self.bowling_rating
        }
    
    def _update_ratings(self):
        """Update Elo-style ratings based on performance"""
        if self.matches_played == 0:
            return
        
        # Simple rating calculation based on win rate
        win_rate = self.wins / self.matches_played if self.matches_played > 0 else 0
        
        # Base rating adjustment
        rating_adjustment = (win_rate - 0.5) * 200  # Adjust by up to ±100 points
        self.rating = max(800, min(1200, 1000 + rating_adjustment))
        
        # Batting rating based on runs per match
        if self.matches_played > 0:
            runs_per_match = self.runs / self.matches_played
            batting_adjustment = (runs_per_match - 20) * 5  # Adjust based on 20 runs per match baseline
            self.batting_rating = max(800, min(1200, 1000 + batting_adjustment))
        
        # Bowling rating based on wickets per match
        if self.matches_played > 0:
            wickets_per_match = self.wickets / self.matches_played
            bowling_adjustment = (wickets_per_match - 2) * 50  # Adjust based on 2 wickets per match baseline
            self.bowling_rating = max(800, min(1200, 1000 + bowling_adjustment))
    
    def get_win_rate(self):
        """Get win rate percentage"""
        if self.matches_played == 0:
            return 0
        return (self.wins / self.matches_played) * 100
    
    def get_batting_average(self):
        """Calculate batting average: Total Runs ÷ (Total Innings - Not Outs)"""
        # For simplicity, we'll use matches_played as innings
        # In real cricket, you'd track not-outs separately
        if self.matches_played == 0:
            return 0.0
        return round(self.runs / self.matches_played, 2)
    
    def get_bowling_average(self):
        """Calculate bowling average: Total Runs Conceded ÷ Total Wickets"""
        # For this system, we'll use a simplified approach
        # In real cricket, you'd track runs conceded separately
        if self.wickets == 0:
            return 0.0
        # Estimate runs conceded based on wickets (simplified)
        # In a real system, you'd track this properly
        estimated_runs_conceded = self.wickets * 15  # Rough estimate
        return round(estimated_runs_conceded / self.wickets, 2)
    
    def get_avg_runs_per_match(self):
        """Get average runs per match (for backward compatibility)"""
        return self.get_batting_average()
    
    def get_avg_wickets_per_match(self):
        """Get average wickets per match (for backward compatibility)"""
        if self.matches_played == 0:
            return 0.0
        return round(self.wickets / self.matches_played, 2)
    
    def get_rank(self):
        """Get the user's current rank based on rating"""
        from django.db.models import F
        
        # Get all active users with profiles, sorted by rating
        all_profiles = Profile.objects.filter(
            user__is_deleted=False,
            matches_played__gt=0
        ).order_by('-rating', '-matches_played', '-wins')
        
        # Find the rank of this profile
        rank = 1
        for profile in all_profiles:
            if profile.id == self.id:
                return rank
            rank += 1
        
        return rank
    
    def get_recent_matches(self, limit=5):
        """Get recent completed matches"""
        from tampere_cricket.matches.models import Challenge
        from django.db.models import F, Case, When, Value
        from django.db.models.functions import Coalesce
        
        return Challenge.objects.filter(
            models.Q(challenger=self.user) | models.Q(opponent=self.user),
            status='COMPLETED'
        ).order_by(
            '-completed_at',  # Primary: completed_at (most recent first)
            '-scheduled_at',  # Secondary: scheduled_at if completed_at is null
            '-created_at'    # Tertiary: created_at if both are null
        )[:limit]
    
    def get_performance_trend(self, days=30):
        """Get performance trend over last N days"""
        from tampere_cricket.matches.models import Challenge
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        recent_challenges = Challenge.objects.filter(
            models.Q(challenger=self.user) | models.Q(opponent=self.user),
            status='COMPLETED',
            completed_at__gte=start_date
        ).order_by('completed_at')
        
        trend_data = []
        cumulative_wins = 0
        cumulative_matches = 0
        
        for challenge in recent_challenges:
            cumulative_matches += 1
            if challenge.winner == self.user:
                cumulative_wins += 1
            
            win_rate = (cumulative_wins / cumulative_matches) * 100 if cumulative_matches > 0 else 0
            trend_data.append({
                'date': challenge.completed_at.date(),
                'win_rate': win_rate,
                'matches': cumulative_matches
            })
        
        return trend_data