from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, User
from tampere_cricket.matches.models import MatchResult, Challenge


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a User is created"""
    if created:
        Profile.objects.create(
            user=instance,
            ranking_change_batting=0,
            ranking_change_bowling=0,
            ranking_change_overall=0,
            previous_batting_rank=0,
            previous_bowling_rank=0,
            previous_overall_rank=0
        )


@receiver(post_save, sender=MatchResult)
def update_user_statistics(sender, instance, created, **kwargs):
    """Automatically update user statistics when match results are saved"""
    if instance.challenge and instance.challenge.status == 'COMPLETED':
        # Update statistics for both challenger and opponent
        challenger_profile, _ = Profile.objects.get_or_create(
            user=instance.challenge.challenger,
            defaults={
                'ranking_change_batting': 0,
                'ranking_change_bowling': 0,
                'ranking_change_overall': 0,
                'previous_batting_rank': 0,
                'previous_bowling_rank': 0,
                'previous_overall_rank': 0
            }
        )
        challenger_profile.update_statistics()
        
        if instance.challenge.opponent:
            opponent_profile, _ = Profile.objects.get_or_create(
                user=instance.challenge.opponent,
                defaults={
                    'ranking_change_batting': 0,
                    'ranking_change_bowling': 0,
                    'ranking_change_overall': 0,
                    'previous_batting_rank': 0,
                    'previous_bowling_rank': 0,
                    'previous_overall_rank': 0
                }
            )
            opponent_profile.update_statistics()


@receiver(post_save, sender=Challenge)
def update_challenge_completion_stats(sender, instance, created, **kwargs):
    """Update statistics when challenge status changes to completed"""
    if instance.status == 'COMPLETED' and instance.winner:
        # Update statistics for both players
        challenger_profile, _ = Profile.objects.get_or_create(
            user=instance.challenger,
            defaults={
                'ranking_change_batting': 0,
                'ranking_change_bowling': 0,
                'ranking_change_overall': 0,
                'previous_batting_rank': 0,
                'previous_bowling_rank': 0,
                'previous_overall_rank': 0
            }
        )
        challenger_profile.update_statistics()
        
        if instance.opponent:
            opponent_profile, _ = Profile.objects.get_or_create(
                user=instance.opponent,
                defaults={
                    'ranking_change_batting': 0,
                    'ranking_change_bowling': 0,
                    'ranking_change_overall': 0,
                    'previous_batting_rank': 0,
                    'previous_bowling_rank': 0,
                    'previous_overall_rank': 0
                }
            )
            opponent_profile.update_statistics()
