from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time

User = get_user_model()


class Challenge(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    
    CHALLENGE_TYPE_CHOICES = [
        ("SINGLE_WICKET", "Single Wicket"),
        ("BATTING", "Batting Challenge"),
        ("BOWLING", "Bowling Challenge"),
    ]
    
    challenger = models.ForeignKey(User, on_delete=models.PROTECT, related_name='challenges_made')
    opponent = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='challenges_received', null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='challenges_won', null=True, blank=True)
    
    # Single Wicket Challenge participants
    team1_batter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='team1_batter_challenges', null=True, blank=True)
    team1_bowler = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='team1_bowler_challenges', null=True, blank=True)
    team2_batter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='team2_batter_challenges', null=True, blank=True)
    team2_bowler = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='team2_bowler_challenges', null=True, blank=True)
    
    # Single Wicket Challenge acceptance tracking
    team1_batter_accepted = models.BooleanField(default=False)
    team1_bowler_accepted = models.BooleanField(default=False)
    team2_batter_accepted = models.BooleanField(default=False)
    team2_bowler_accepted = models.BooleanField(default=False)
    ground = models.ForeignKey('grounds.Ground', on_delete=models.CASCADE, null=True, blank=True)
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES, default="SINGLE_WICKET")
    condition_text = models.TextField(blank=True, help_text="Special conditions or rules for this challenge")
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", default=15, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    description = models.TextField(blank=True)
    
    # Challenge metrics fields
    metric = models.CharField(max_length=100, blank=True, help_text="Challenge metric (e.g., 'Runs', 'Wickets', 'Sixes')")
    target_value = models.PositiveIntegerField(null=True, blank=True, help_text="Target value for the metric")
    over_count = models.PositiveIntegerField(null=True, blank=True, help_text="Number of overs for the challenge")
    summary = models.TextField(blank=True, help_text="Additional comments or summary")
    
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        if self.challenge_type == 'SINGLE_WICKET':
            try:
                team1_batter_name = self.team1_batter.username if self.team1_batter else 'TBD'
                team1_bowler_name = self.team1_bowler.username if self.team1_bowler else 'TBD'
                team2_batter_name = self.team2_batter.username if self.team2_batter else 'TBD'
                team2_bowler_name = self.team2_bowler.username if self.team2_bowler else 'TBD'
                return f"Team 1 ({team1_batter_name} & {team1_bowler_name}) vs Team 2 ({team2_batter_name} & {team2_bowler_name})"
            except:
                return "Single Wicket Challenge"
        else:
            try:
                challenger_name = self.challenger.username if self.challenger else 'Unknown'
            except:
                challenger_name = 'Unknown'
            
            try:
                opponent_name = self.opponent.username if self.opponent else 'TBD'
            except:
                opponent_name = 'TBD'
                
            return f"{challenger_name} vs {opponent_name}"
    
    def get_participants(self):
        """Get all participants in the challenge"""
        if self.challenge_type == 'SINGLE_WICKET':
            participants = []
            if self.team1_batter:
                participants.append(self.team1_batter)
            if self.team1_bowler:
                participants.append(self.team1_bowler)
            if self.team2_batter:
                participants.append(self.team2_batter)
            if self.team2_bowler:
                participants.append(self.team2_bowler)
            return participants
        else:
            participants = [self.challenger]
            if self.opponent:
                participants.append(self.opponent)
            return participants
    
    def get_batters(self):
        """Get all batters in the challenge"""
        if self.challenge_type == 'SINGLE_WICKET':
            batters = []
            if self.team1_batter:
                batters.append(self.team1_batter)
            if self.team2_batter:
                batters.append(self.team2_batter)
            return batters
        else:
            return [self.challenger] if self.challenger else []
    
    def get_bowlers(self):
        """Get all bowlers in the challenge"""
        if self.challenge_type == 'SINGLE_WICKET':
            bowlers = []
            if self.team1_bowler:
                bowlers.append(self.team1_bowler)
            if self.team2_bowler:
                bowlers.append(self.team2_bowler)
            return bowlers
        else:
            return [self.opponent] if self.opponent else []
    
    def all_participants_accepted(self):
        """Check if all participants have accepted the challenge"""
        if self.challenge_type == 'SINGLE_WICKET':
            # Check if all 4 participants have accepted
            return (self.team1_batter_accepted and 
                    self.team1_bowler_accepted and 
                    self.team2_batter_accepted and 
                    self.team2_bowler_accepted)
        else:
            # For regular challenges, just check if opponent accepted
            return self.status == 'ACCEPTED'
    
    def get_participant_acceptance_status(self):
        """Get acceptance status for all participants"""
        if self.challenge_type == 'SINGLE_WICKET':
            return {
                'team1_batter': {
                    'user': self.team1_batter,
                    'accepted': self.team1_batter_accepted
                },
                'team1_bowler': {
                    'user': self.team1_bowler,
                    'accepted': self.team1_bowler_accepted
                },
                'team2_batter': {
                    'user': self.team2_batter,
                    'accepted': self.team2_batter_accepted
                },
                'team2_bowler': {
                    'user': self.team2_bowler,
                    'accepted': self.team2_bowler_accepted
                }
            }
        else:
            return {
                'challenger': {
                    'user': self.challenger,
                    'accepted': True  # Challenger is always considered accepted
                },
                'opponent': {
                    'user': self.opponent,
                    'accepted': self.status == 'ACCEPTED'
                }
            }

    def clean(self):
        if self.date and self.date < timezone.now().date():
            raise ValidationError("Challenge date cannot be in the past")
        
        # Only check self-challenge if both challenger and opponent are set
        try:
            if self.opponent and self.challenger and self.opponent == self.challenger:
                raise ValidationError("You cannot challenge yourself")
        except:
            # If challenger is not set yet, skip this check
            pass
        
        # Single wicket challenge validation
        if self.challenge_type == 'SINGLE_WICKET':
            # Allow participants to be the same person - no validation needed
            # This allows flexibility for players to take multiple roles
            pass
    
    def get_display_name_for_user(self, user):
        """Get display name for a user, handling soft-deleted users"""
        if user:
            return user.get_display_name()
        else:
            return "Unknown"
    
    def get_challenger_display_name(self):
        """Get challenger display name, handling soft-deleted users"""
        return self.get_display_name_for_user(self.challenger)
    
    def get_opponent_display_name(self):
        """Get opponent display name, handling soft-deleted users"""
        return self.get_display_name_for_user(self.opponent)
    
    def get_winner_display_name(self):
        """Get winner display name, handling soft-deleted users"""
        return self.get_display_name_for_user(self.winner)
    
    def has_deleted_participants(self):
        """Check if any participants are soft-deleted"""
        participants = self.get_participants()
        return any(user.is_deleted for user in participants if user)
    
    def get_active_participants(self):
        """Get only active (non-deleted) participants"""
        participants = self.get_participants()
        return [user for user in participants if user and not user.is_deleted]


class TimeSlot(models.Model):
    ground = models.ForeignKey('grounds.Ground', on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.ground.name} - {self.date} {self.start_time}-{self.end_time}"
    
    class Meta:
        unique_together = ['ground', 'date', 'start_time']


class MatchResult(models.Model):
    """Model to store match results and statistics"""
    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE, related_name='match_result')
    
    # Match Statistics
    challenger_runs = models.PositiveIntegerField(default=0, help_text="Runs scored by challenger")
    challenger_wickets = models.PositiveIntegerField(default=0, help_text="Wickets taken by challenger")
    challenger_sixes = models.PositiveIntegerField(default=0, help_text="Sixes hit by challenger")
    challenger_fours = models.PositiveIntegerField(default=0, help_text="Fours hit by challenger")
    challenger_dots = models.PositiveIntegerField(default=0, help_text="Dot balls bowled by challenger")
    
    opponent_runs = models.PositiveIntegerField(default=0, help_text="Runs scored by opponent")
    opponent_wickets = models.PositiveIntegerField(default=0, help_text="Wickets taken by opponent")
    opponent_sixes = models.PositiveIntegerField(default=0, help_text="Sixes hit by opponent")
    opponent_fours = models.PositiveIntegerField(default=0, help_text="Fours hit by opponent")
    opponent_dots = models.PositiveIntegerField(default=0, help_text="Dot balls bowled by opponent")
    
    # Match Details
    total_overs = models.PositiveIntegerField(default=0, help_text="Total overs played")
    match_duration = models.PositiveIntegerField(default=0, help_text="Match duration in minutes")
    weather_conditions = models.CharField(max_length=100, blank=True, help_text="Weather conditions during match")
    pitch_conditions = models.CharField(max_length=100, blank=True, help_text="Pitch conditions")
    
    # Admin Fields
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='match_results_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Match Notes
    notes = models.TextField(blank=True, help_text="Additional match notes or comments")
    
    def __str__(self):
        return f"Match Result: {self.challenge.get_challenger_display_name()} vs {self.challenge.get_opponent_display_name() if self.challenge.opponent else 'Open Challenge'}"
    
    def get_challenger_score(self):
        """Get challenger's total score based on challenge metric"""
        if self.challenge.metric == 'runs':
            return self.challenger_runs
        elif self.challenge.metric == 'wickets':
            return self.challenger_wickets
        elif self.challenge.metric == 'sixes':
            return self.challenger_sixes
        elif self.challenge.metric == 'fours':
            return self.challenger_fours
        elif self.challenge.metric == 'dots':
            return self.challenger_dots
        return 0
    
    def get_opponent_score(self):
        """Get opponent's total score based on challenge metric"""
        if self.challenge.metric == 'runs':
            return self.opponent_runs
        elif self.challenge.metric == 'wickets':
            return self.opponent_wickets
        elif self.challenge.metric == 'sixes':
            return self.opponent_sixes
        elif self.challenge.metric == 'fours':
            return self.opponent_fours
        elif self.challenge.metric == 'dots':
            return self.opponent_dots
        return 0
    
    def determine_winner(self):
        """Determine winner based on challenge metric and target"""
        if self.challenge.challenge_type == 'SINGLE_WICKET':
            # For single wicket challenges, compare batter runs
            team1_batter_runs = self.challenger_runs or 0
            team2_batter_runs = self.opponent_runs or 0
            
            if team1_batter_runs > team2_batter_runs:
                return self.challenge.team1_batter
            elif team2_batter_runs > team1_batter_runs:
                return self.challenge.team2_batter
            else:
                # Tie - return None for draw
                return None
        else:
            # Regular challenge logic
            challenger_score = self.get_challenger_score() or 0
            opponent_score = self.get_opponent_score() or 0
            target = self.challenge.target_value
            
            # If no target is set, winner is whoever scored higher
            if target is None:
                return self.challenge.challenger if challenger_score > opponent_score else self.challenge.opponent
            
            # If both met target, winner is whoever scored higher
            if challenger_score >= target and opponent_score >= target:
                return self.challenge.challenger if challenger_score > opponent_score else self.challenge.opponent
            elif challenger_score >= target:
                return self.challenge.challenger
            elif opponent_score >= target:
                return self.challenge.opponent
            else:
                # Neither met target, winner is whoever scored higher
                return self.challenge.challenger if challenger_score > opponent_score else self.challenge.opponent
    
    class Meta:
        verbose_name = "Match Result"
        verbose_name_plural = "Match Results"
