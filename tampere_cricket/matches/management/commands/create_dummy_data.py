from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from tampere_cricket.matches.models import Challenge, TimeSlot
from tampere_cricket.accounts.models import User
from tampere_cricket.grounds.models import Ground

class Command(BaseCommand):
    help = 'Create dummy data for testing ChallengeHub'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--challenges',
            type=int,
            default=20,
            help='Number of challenges to create (default: 20)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to create time slots for (default: 30)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting dummy data creation...'))
        
        # Create users
        users = self.create_users(options['users'])
        
        # Create time slots
        time_slots = self.create_timeslots(options['days'])
        
        # Create challenges
        challenges = self.create_challenges(users, time_slots, options['challenges'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(users)} users\n'
                f'- {len(time_slots)} time slots\n'
                f'- {len(challenges)} challenges'
            )
        )

    def create_users(self, count):
        """Create dummy users with profiles"""
        self.stdout.write('Creating users...')
        
        users_data = [
            {'username': 'john_cricketer', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'sarah_batter', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson'},
            {'username': 'mike_bowler', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'alex_allrounder', 'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Brown'},
            {'username': 'emma_wicketkeeper', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Davis'},
            {'username': 'david_captain', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Miller'},
            {'username': 'lisa_opener', 'email': 'lisa@example.com', 'first_name': 'Lisa', 'last_name': 'Garcia'},
            {'username': 'tom_spinner', 'email': 'tom@example.com', 'first_name': 'Tom', 'last_name': 'Anderson'},
            {'username': 'anna_fast', 'email': 'anna@example.com', 'first_name': 'Anna', 'last_name': 'Taylor'},
            {'username': 'chris_medium', 'email': 'chris@example.com', 'first_name': 'Chris', 'last_name': 'Thomas'},
        ]
        
        created_users = []
        for i, user_data in enumerate(users_data[:count]):
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')
            else:
                self.stdout.write(f'  User already exists: {user.username}')
            
            # Update user profile fields
            user.phone = f'+123456789{random.randint(10, 99)}'
            user.role = random.choice(['batter', 'bowler', 'allrounder'])
            user.preferred_batting_style = random.choice(['right_handed', 'left_handed'])
            user.preferred_bowling_style = random.choice([
                'right_arm_fast', 'right_arm_medium', 'right_arm_spin',
                'left_arm_fast', 'left_arm_medium', 'left_arm_spin',
                'leg_spin', 'off_spin'
            ])
            user.save()
            created_users.append(user)
        
        return created_users

    def create_timeslots(self, days):
        """Create dummy time slots for different dates"""
        self.stdout.write('Creating time slots...')
        
        # Get available grounds
        grounds = list(Ground.objects.all())
        if not grounds:
            self.stdout.write(self.style.WARNING('No grounds found. Please create grounds first.'))
            return []
        
        base_date = timezone.now().date()
        time_slots = []
        created_count = 0
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Create 3-5 time slots per day per ground
            num_slots = random.randint(3, 5)
            for j in range(num_slots):
                hour = random.randint(9, 18)  # Between 9 AM and 6 PM
                minute = random.choice([0, 30])  # On the hour or half hour
                
                # Choose a random ground
                ground = random.choice(grounds)
                
                time_slot, created = TimeSlot.objects.get_or_create(
                    ground=ground,
                    date=date,
                    start_time=f"{hour:02d}:{minute:02d}",
                    defaults={
                        'end_time': f"{hour+1:02d}:{minute:02d}",
                        'is_available': True,
                        'price': random.uniform(10.0, 50.0)
                    }
                )
                time_slots.append(time_slot)
                if created:
                    created_count += 1
        
        self.stdout.write(f'  Created {created_count} new time slots (total: {len(time_slots)})')
        return time_slots

    def create_challenges(self, users, time_slots, count):
        """Create dummy challenges of all types"""
        self.stdout.write('Creating challenges...')
        
        challenges = []
        challenge_types = ['SINGLE_WICKET', 'BATTING', 'BOWLING']
        
        for i in range(count):
            challenge_type = random.choice(challenge_types)
            challenger = random.choice(users)
            
            if challenge_type == 'SINGLE_WICKET':
                challenge = self.create_single_wicket_challenge(challenger, time_slots, i)
            elif challenge_type == 'BATTING':
                challenge = self.create_batting_challenge(challenger, time_slots, i)
            else:  # BOWLING
                challenge = self.create_bowling_challenge(challenger, time_slots, i)
            
            challenges.append(challenge)
            self.stdout.write(f'  Created {challenge_type} Challenge: {challenge.id}')
        
        # Set some challenges to different statuses
        self.set_challenge_statuses(challenges)
        
        return challenges

    def create_single_wicket_challenge(self, challenger, time_slots, index):
        """Create a single wicket challenge"""
        time_slot = random.choice(time_slots)
        challenge = Challenge.objects.create(
            challenger=challenger,
            challenge_type='SINGLE_WICKET',
            condition_text=f"Single Wicket Challenge #{index+1}: Best of {random.randint(2, 4)} overs, winner takes all!",
            metric='RUNS',
            target_value=random.randint(20, 50),
            over_count=random.randint(2, 4),
            ground=time_slot.ground,
            date=time_slot.date,
            time=time_slot.start_time,
            status=random.choice(['OPEN', 'PENDING', 'ACCEPTED']),
            summary=f"Exciting single wicket match with {random.randint(2, 4)} overs per team"
        )
        
        # Assign team members
        available_users = [u for u in User.active_objects() if u != challenger]
        if len(available_users) >= 3:
            team1_batter = random.choice(available_users)
            available_users.remove(team1_batter)
            team1_bowler = random.choice(available_users)
            available_users.remove(team1_bowler)
            team2_batter = random.choice(available_users)
            available_users.remove(team2_batter)
            team2_bowler = random.choice(available_users)
            
            challenge.team1_batter = team1_batter
            challenge.team1_bowler = team1_bowler
            challenge.team2_batter = team2_batter
            challenge.team2_bowler = team2_bowler
            challenge.save()
        
        return challenge

    def create_batting_challenge(self, challenger, time_slots, index):
        """Create a batting challenge"""
        time_slot = random.choice(time_slots)
        challenge = Challenge.objects.create(
            challenger=challenger,
            challenge_type='BATTING',
            condition_text=f"Batting Challenge #{index+1}: Score {random.randint(30, 80)} runs in {random.randint(3, 6)} overs!",
            metric='RUNS',
            target_value=random.randint(30, 80),
            over_count=random.randint(3, 6),
            ground=time_slot.ground,
            date=time_slot.date,
            time=time_slot.start_time,
            status=random.choice(['OPEN', 'PENDING', 'ACCEPTED', 'COMPLETED']),
            summary=f"Individual batting challenge - can you score the target runs?"
        )
        
        # Assign opponent
        available_users = [u for u in User.active_objects() if u != challenger]
        if available_users:
            challenge.opponent = random.choice(available_users)
            challenge.save()
        
        return challenge

    def create_bowling_challenge(self, challenger, time_slots, index):
        """Create a bowling challenge"""
        time_slot = random.choice(time_slots)
        challenge = Challenge.objects.create(
            challenger=challenger,
            challenge_type='BOWLING',
            condition_text=f"Bowling Challenge #{index+1}: Take {random.randint(2, 5)} wickets in {random.randint(4, 8)} overs!",
            metric='WICKETS',
            target_value=random.randint(2, 5),
            over_count=random.randint(4, 8),
            ground=time_slot.ground,
            date=time_slot.date,
            time=time_slot.start_time,
            status=random.choice(['OPEN', 'PENDING', 'ACCEPTED', 'COMPLETED']),
            summary=f"Individual bowling challenge - can you take the target wickets?"
        )
        
        # Assign opponent
        available_users = [u for u in User.active_objects() if u != challenger]
        if available_users:
            challenge.opponent = random.choice(available_users)
            challenge.save()
        
        return challenge

    def set_challenge_statuses(self, challenges):
        """Set some challenges to different statuses"""
        # Mark some as completed
        completed_count = min(3, len(challenges) // 4)
        for challenge in random.sample(challenges, completed_count):
            challenge.status = 'COMPLETED'
            challenge.save()
        
        # Mark some as cancelled
        cancelled_count = min(2, len(challenges) // 6)
        for challenge in random.sample(challenges, cancelled_count):
            challenge.status = 'CANCELLED'
            challenge.save()
        
        self.stdout.write(f'  Set {completed_count} challenges as completed')
        self.stdout.write(f'  Set {cancelled_count} challenges as cancelled')
