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
