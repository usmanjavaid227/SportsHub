from django import forms
from django.contrib.auth import get_user_model
from .models import Challenge, MatchResult
from tampere_cricket.grounds.models import Ground

User = get_user_model()


class ChallengeForm(forms.ModelForm):
    """Form for creating and editing challenges"""
    
    # Additional fields for challenge metrics
    metric = forms.ChoiceField(
        choices=[
            ('runs', 'Runs'),
            ('wickets', 'Wickets'),
            ('sixes', 'Sixes'),
            ('fours', 'Fours'),
            ('dots', 'Dot Balls'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    target_value = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '100',
            'placeholder': 'Enter target value'
        })
    )
    
    over_count = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '20',
            'placeholder': 'Number of overs'
        })
    )
    
    # scheduled_date is handled in the clean method to map to the model's date field
    
    summary = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional comments or special conditions (optional)'
        })
    )
    
    # Override duration field to make it optional
    duration = forms.IntegerField(
        required=False,
        initial=15,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '15',
            'max': '300',
            'step': '15',
            'placeholder': 'Duration in minutes (default: 15)'
        })
    )
    
    class Meta:
        model = Challenge
        fields = [
            'opponent', 'challenge_type', 'condition_text', 'ground', 
            'date', 'time', 'description', 'team1_batter', 'team1_bowler', 
            'team2_batter', 'team2_bowler'
        ]
        widgets = {
            'opponent': forms.Select(attrs={'class': 'form-select'}),
            'challenge_type': forms.Select(attrs={'class': 'form-select'}),
            'condition_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your challenge condition (e.g., "I will hit 2 sixes in this over")'
            }),
            'ground': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': '2024-01-01'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional details or comments (optional)'
            }),
            'team1_batter': forms.Select(attrs={'class': 'form-select'}),
            'team1_bowler': forms.Select(attrs={'class': 'form-select'}),
            'team2_batter': forms.Select(attrs={'class': 'form-select'}),
            'team2_bowler': forms.Select(attrs={'class': 'form-select'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter opponents to exclude the current user
        if user:
            self.fields['opponent'].queryset = User.objects.exclude(id=user.id)
        
        # Add labels and help text
        self.fields['opponent'].label = 'Opponent'
        self.fields['opponent'].help_text = 'Select a specific player or "Open to All" for anyone to accept'
        self.fields['opponent'].empty_label = 'Open to All'
        
        self.fields['challenge_type'].label = 'Challenge Type'
        self.fields['challenge_type'].help_text = 'Choose the type of challenge'
        
        self.fields['condition_text'].label = 'Challenge Conditions'
        self.fields['condition_text'].help_text = 'Describe what the challenger must achieve'
        
        self.fields['ground'].label = 'Ground'
        self.fields['ground'].help_text = 'Select the ground for the challenge'
        self.fields['ground'].empty_label = 'Select a ground'
        
        self.fields['date'].label = 'Challenge Date'
        self.fields['date'].help_text = 'When do you want to play this challenge?'
        
        self.fields['time'].label = 'Start Time'
        self.fields['time'].help_text = 'What time should the challenge start?'
        
        self.fields['duration'].label = 'Duration (minutes)'
        self.fields['duration'].help_text = 'How long should the challenge last?'
        
        self.fields['description'].label = 'Additional Details'
        self.fields['description'].required = False
        
        # New fields labels and help text
        self.fields['metric'].label = 'Challenge Metric'
        self.fields['metric'].help_text = 'What will be measured? (e.g., Runs, Wickets, Sixes)'
        self.fields['metric'].required = False
        
        self.fields['target_value'].label = 'Target Value'
        self.fields['target_value'].help_text = 'What is the target to achieve?'
        self.fields['target_value'].required = False
        
        self.fields['over_count'].label = 'Number of Overs'
        self.fields['over_count'].help_text = 'How many overs for this challenge?'
        self.fields['over_count'].required = False
        
        # Single Wicket Challenge fields
        self.fields['team1_batter'].label = 'Team 1 - Batter'
        self.fields['team1_batter'].help_text = 'Select the batter for Team 1'
        self.fields['team1_batter'].empty_label = 'Select Team 1 Batter'
        self.fields['team1_batter'].required = False
        
        self.fields['team1_bowler'].label = 'Team 1 - Bowler'
        self.fields['team1_bowler'].help_text = 'Select the bowler for Team 1'
        self.fields['team1_bowler'].empty_label = 'Select Team 1 Bowler'
        self.fields['team1_bowler'].required = False
        
        self.fields['team2_batter'].label = 'Team 2 - Batter'
        self.fields['team2_batter'].help_text = 'Select the batter for Team 2'
        self.fields['team2_batter'].empty_label = 'Select Team 2 Batter'
        self.fields['team2_batter'].required = False
        
        self.fields['team2_bowler'].label = 'Team 2 - Bowler'
        self.fields['team2_bowler'].help_text = 'Select the bowler for Team 2'
        self.fields['team2_bowler'].empty_label = 'Select Team 2 Bowler'
        self.fields['team2_bowler'].required = False
        
        # Set querysets for all user fields - allow same user to be selected multiple times
        if user:
            user_queryset = User.objects.exclude(id=user.id)
            self.fields['team1_batter'].queryset = user_queryset
            self.fields['team1_bowler'].queryset = user_queryset
            self.fields['team2_batter'].queryset = user_queryset
            self.fields['team2_bowler'].queryset = user_queryset
    
    def save(self, commit=True):
        challenge = super().save(commit=False)
        # The challenger will be set in the view
        if commit:
            challenge.save()
        return challenge
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        duration = cleaned_data.get('duration')
        challenge_type = cleaned_data.get('challenge_type')
        
        # Set scheduled_at if both date and time are provided
        if date and time:
            from django.utils import timezone
            from datetime import datetime
            scheduled_at = datetime.combine(date, time)
            cleaned_data['scheduled_at'] = scheduled_at
        
        # Set default duration if not provided
        if not duration:
            cleaned_data['duration'] = 15  # Default 15 minutes
        
        # Validate Single Wicket team selections
        if challenge_type == 'SINGLE_WICKET':
            team1_batter = cleaned_data.get('team1_batter')
            team1_bowler = cleaned_data.get('team1_bowler')
            team2_batter = cleaned_data.get('team2_batter')
            team2_bowler = cleaned_data.get('team2_bowler')
            
            # Check if any player is selected in both teams
            if team1_batter and team1_batter == team2_batter:
                raise forms.ValidationError('Team 1 Batter cannot be the same as Team 2 Batter')
            
            if team1_batter and team1_batter == team2_bowler:
                raise forms.ValidationError('Team 1 Batter cannot be the same as Team 2 Bowler')
            
            if team1_bowler and team1_bowler == team2_batter:
                raise forms.ValidationError('Team 1 Bowler cannot be the same as Team 2 Batter')
            
            if team1_bowler and team1_bowler == team2_bowler:
                raise forms.ValidationError('Team 1 Bowler cannot be the same as Team 2 Bowler')
        
        return cleaned_data


class MatchResultForm(forms.ModelForm):
    """Form for updating match results and statistics - Admin only"""
    
    # Manual winner selection
    manual_winner = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        help_text="Select winner manually (optional - leave empty for automatic determination)"
    )
    
    class Meta:
        model = MatchResult
        fields = [
            'challenger_runs', 'challenger_wickets', 'challenger_sixes', 'challenger_fours', 'challenger_dots',
            'opponent_runs', 'opponent_wickets', 'opponent_sixes', 'opponent_fours', 'opponent_dots',
            'total_overs', 'match_duration', 'weather_conditions', 'pitch_conditions', 'notes'
        ]
        widgets = {
            'challenger_runs': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Runs scored'}),
            'challenger_wickets': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Wickets taken'}),
            'challenger_sixes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Sixes hit'}),
            'challenger_fours': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Fours hit'}),
            'challenger_dots': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Dot balls bowled'}),
            'opponent_runs': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Runs scored'}),
            'opponent_wickets': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Wickets taken'}),
            'opponent_sixes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Sixes hit'}),
            'opponent_fours': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Fours hit'}),
            'opponent_dots': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Dot balls bowled'}),
            'total_overs': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Total overs played'}),
            'match_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Duration in minutes'}),
            'weather_conditions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sunny, Cloudy, Rainy'}),
            'pitch_conditions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dry, Wet, Bouncy'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional match notes or comments'})
        }
    
    def __init__(self, *args, **kwargs):
        challenge = kwargs.pop('challenge', None)
        super().__init__(*args, **kwargs)
        
        if challenge:
            # Set labels based on challenge participants
            self.fields['challenger_runs'].label = f"{challenge.challenger.username} - Runs"
            self.fields['challenger_wickets'].label = f"{challenge.challenger.username} - Wickets"
            self.fields['challenger_sixes'].label = f"{challenge.challenger.username} - Sixes"
            self.fields['challenger_fours'].label = f"{challenge.challenger.username} - Fours"
            self.fields['challenger_dots'].label = f"{challenge.challenger.username} - Dot Balls"
            
            # Set up manual winner choices
            winner_choices = [
                ('', 'Automatic (based on statistics)'),
                (str(challenge.challenger.id), f"{challenge.challenger.username} (Challenger)")
            ]
            if challenge.opponent:
                winner_choices.append((str(challenge.opponent.id), f"{challenge.opponent.username} (Opponent)"))
                self.fields['opponent_runs'].label = f"{challenge.opponent.username} - Runs"
                self.fields['opponent_wickets'].label = f"{challenge.opponent.username} - Wickets"
                self.fields['opponent_sixes'].label = f"{challenge.opponent.username} - Sixes"
                self.fields['opponent_fours'].label = f"{challenge.opponent.username} - Fours"
                self.fields['opponent_dots'].label = f"{challenge.opponent.username} - Dot Balls"
            else:
                # Hide opponent fields for open challenges
                for field_name in ['opponent_runs', 'opponent_wickets', 'opponent_sixes', 'opponent_fours', 'opponent_dots']:
                    self.fields[field_name].widget = forms.HiddenInput()
            
            self.fields['manual_winner'].choices = winner_choices
        
        # Add help text for key fields
        self.fields['total_overs'].help_text = "Total overs played in the match"
        self.fields['match_duration'].help_text = "Actual match duration in minutes"
        self.fields['weather_conditions'].help_text = "Weather conditions during the match"
        self.fields['pitch_conditions'].help_text = "Pitch conditions and characteristics"
        self.fields['notes'].help_text = "Additional notes about the match"
