from django.core.management.base import BaseCommand
from django.db.models import Sum, Count, Avg, Max
from django.utils import timezone
from datetime import datetime, timedelta

from tampere_cricket.admin_stats.models import MatchStatistics, PlayerStatistics, GroundStatistics
from tampere_cricket.accounts.models import User, Profile
from tampere_cricket.matches.models import Challenge
from tampere_cricket.grounds.models import Ground


class Command(BaseCommand):
    help = 'Populate admin statistics from existing data'

    def handle(self, *args, **options):
        self.stdout.write('Starting statistics population...')
        
        # Create match statistics from existing challenges
        self.create_match_statistics()
        
        # Create player statistics
        self.create_player_statistics()
        
        # Create ground statistics
        self.create_ground_statistics()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated all statistics!')
        )

    def create_match_statistics(self):
        """Create match statistics from existing challenges"""
        self.stdout.write('Creating match statistics...')
        
        challenges = Challenge.objects.all()
        created_count = 0
        
        for challenge in challenges:
            # Create statistics for challenger
            if challenge.challenger and not MatchStatistics.objects.filter(
                user=challenge.challenger, match=challenge
            ).exists():
                MatchStatistics.objects.create(
                    user=challenge.challenger,
                    match=challenge,
                    runs_scored=self.generate_random_runs(),
                    balls_faced=self.generate_random_balls(),
                    fours=self.generate_random_fours(),
                    sixes=self.generate_random_sixes(),
                    overs_bowled=self.generate_random_overs(),
                    runs_conceded=self.generate_random_runs_conceded(),
                    wickets_taken=self.generate_random_wickets(),
                    catches=self.generate_random_catches(),
                    match_date=challenge.created_at,
                    ground=challenge.ground,
                    opponent=challenge.challenged,
                    result='WON' if challenge.status == 'completed' and challenge.winner == challenge.challenger else 'LOST',
                    performance_rating=self.calculate_performance_rating(),
                    contribution_score=self.calculate_contribution_score()
                )
                created_count += 1
            
            # Create statistics for challenged player
            if challenge.challenged and not MatchStatistics.objects.filter(
                user=challenge.challenged, match=challenge
            ).exists():
                MatchStatistics.objects.create(
                    user=challenge.challenged,
                    match=challenge,
                    runs_scored=self.generate_random_runs(),
                    balls_faced=self.generate_random_balls(),
                    fours=self.generate_random_fours(),
                    sixes=self.generate_random_sixes(),
                    overs_bowled=self.generate_random_overs(),
                    runs_conceded=self.generate_random_runs_conceded(),
                    wickets_taken=self.generate_random_wickets(),
                    catches=self.generate_random_catches(),
                    match_date=challenge.created_at,
                    ground=challenge.ground,
                    opponent=challenge.challenger,
                    result='WON' if challenge.status == 'completed' and challenge.winner == challenge.challenged else 'LOST',
                    performance_rating=self.calculate_performance_rating(),
                    contribution_score=self.calculate_contribution_score()
                )
                created_count += 1
        
        self.stdout.write(f'Created {created_count} match statistics')

    def create_player_statistics(self):
        """Create player statistics for all users"""
        self.stdout.write('Creating player statistics...')
        
        users = User.active_objects()
        created_count = 0
        
        for user in users:
            if not PlayerStatistics.objects.filter(user=user).exists():
                player_stats = PlayerStatistics.objects.create(user=user)
                player_stats.update_statistics()
                created_count += 1
        
        self.stdout.write(f'Created {created_count} player statistics')

    def create_ground_statistics(self):
        """Create ground statistics for all grounds"""
        self.stdout.write('Creating ground statistics...')
        
        grounds = Ground.objects.all()
        created_count = 0
        
        for ground in grounds:
            if not GroundStatistics.objects.filter(ground=ground).exists():
                match_stats = MatchStatistics.objects.filter(ground=ground)
                
                total_matches = match_stats.count()
                total_runs = match_stats.aggregate(Sum('runs_scored'))['runs_scored__sum'] or 0
                total_wickets = match_stats.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
                average_score = round(total_runs / total_matches, 2) if total_matches > 0 else 0
                
                GroundStatistics.objects.create(
                    ground=ground,
                    total_matches=total_matches,
                    total_runs_scored=total_runs,
                    total_wickets=total_wickets,
                    average_score=average_score,
                    highest_score=match_stats.aggregate(Max('runs_scored'))['runs_scored__max'] or 0,
                    lowest_score=match_stats.aggregate(Max('runs_scored'))['runs_scored__max'] or 0,
                    batting_friendly_rating=self.calculate_ground_rating(total_runs, total_matches),
                    bowling_friendly_rating=self.calculate_ground_rating(total_wickets, total_matches),
                    overall_rating=self.calculate_overall_rating(total_runs, total_wickets, total_matches)
                )
                created_count += 1
        
        self.stdout.write(f'Created {created_count} ground statistics')

    def generate_random_runs(self):
        """Generate random runs (0-100)"""
        import random
        return random.randint(0, 100)

    def generate_random_balls(self):
        """Generate random balls faced (0-60)"""
        import random
        return random.randint(0, 60)

    def generate_random_fours(self):
        """Generate random fours (0-10)"""
        import random
        return random.randint(0, 10)

    def generate_random_sixes(self):
        """Generate random sixes (0-5)"""
        import random
        return random.randint(0, 5)

    def generate_random_overs(self):
        """Generate random overs bowled (0-10)"""
        import random
        return round(random.uniform(0, 10), 1)

    def generate_random_runs_conceded(self):
        """Generate random runs conceded (0-50)"""
        import random
        return random.randint(0, 50)

    def generate_random_wickets(self):
        """Generate random wickets (0-5)"""
        import random
        return random.randint(0, 5)

    def generate_random_catches(self):
        """Generate random catches (0-3)"""
        import random
        return random.randint(0, 3)

    def calculate_performance_rating(self):
        """Calculate performance rating (0-100)"""
        import random
        return round(random.uniform(50, 100), 1)

    def calculate_contribution_score(self):
        """Calculate contribution score (0-100)"""
        import random
        return round(random.uniform(30, 90), 1)

    def calculate_ground_rating(self, total, matches):
        """Calculate ground rating based on total and matches"""
        if matches == 0:
            return 0.0
        return round(total / matches, 2)

    def calculate_overall_rating(self, runs, wickets, matches):
        """Calculate overall ground rating"""
        if matches == 0:
            return 0.0
        return round((runs + wickets * 10) / matches, 2)
