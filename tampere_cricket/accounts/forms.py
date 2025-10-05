from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'city',
            'bio',
            'role',
            'experience_level',
            'preferred_batting_style',
            'preferred_bowling_style',
            'years_playing',
            'avatar'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'role': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'experience_level': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'preferred_batting_style': forms.Select(attrs={'class': 'form-select'}),
            'preferred_bowling_style': forms.Select(attrs={'class': 'form-select'}),
            'years_playing': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'required': True}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['city'].required = True
        self.fields['bio'].required = True
        self.fields['role'].required = True
        self.fields['experience_level'].required = True
        self.fields['years_playing'].required = True

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

    def clean_years_playing(self):
        years = self.cleaned_data.get('years_playing')
        if years and years > 50:
            raise forms.ValidationError("Please enter a realistic number of years.")
        return years


class ProfileCompletionForm(forms.ModelForm):
    """Form for checking profile completion status"""
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'city',
            'bio',
            'role',
            'experience_level',
            'years_playing'
        ]

    def is_profile_complete(self):
        """Check if all required profile fields are filled"""
        required_fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'city', 'bio', 'role', 'experience_level', 'years_playing'
        ]
        
        for field in required_fields:
            value = getattr(self.instance, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                return False
        return True