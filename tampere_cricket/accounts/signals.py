from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from tampere_cricket.matches.models import MatchResult, Challenge


@receiver(post_save, sender=MatchResult)
def update_user_statistics(sender, instance, created, **kwargs):
    """Automatically update user statistics when match results are saved"""
    if instance.challenge and instance.challenge.status == 'COMPLETED':
        # Update statistics for both challenger and opponent
        challenger_profile, _ = Profile.objects.get_or_create(user=instance.challenge.challenger)
        challenger_profile.update_statistics()
        
        if instance.challenge.opponent:
            opponent_profile, _ = Profile.objects.get_or_create(user=instance.challenge.opponent)
            opponent_profile.update_statistics()


@receiver(post_save, sender=Challenge)
def update_challenge_completion_stats(sender, instance, created, **kwargs):
    """Update statistics when challenge status changes to completed"""
    if instance.status == 'COMPLETED' and instance.winner:
        # Update statistics for both players
        challenger_profile, _ = Profile.objects.get_or_create(user=instance.challenger)
        challenger_profile.update_statistics()
        
        if instance.opponent:
            opponent_profile, _ = Profile.objects.get_or_create(user=instance.opponent)
            opponent_profile.update_statistics()
