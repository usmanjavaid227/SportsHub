from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
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
            'role',
            'preferred_batting_style',
            'preferred_bowling_style',
            'avatar'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'preferred_batting_style': forms.Select(attrs={'class': 'form-select'}),
            'preferred_bowling_style': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make only mandatory fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        # All other fields are optional

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


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
            'role',
            'preferred_batting_style',
            'preferred_bowling_style'
        ]

    def is_profile_complete(self):
        """Check if all required profile fields are filled"""
        required_fields = [
            'first_name', 'last_name', 'email', 'phone'
        ]
        
        for field in required_fields:
            value = getattr(self.instance, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                return False
        return True


class PasswordChangeForm(forms.Form):
    """Form for changing user password"""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': True
        }),
        label='Current Password',
        required=True
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': True
        }),
        label='New Password',
        required=True,
        min_length=8
    )
    
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': True
        }),
        label='Confirm New Password',
        required=True
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        """Validate current password"""
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password
    
    def clean_confirm_password(self):
        """Validate password confirmation"""
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('New passwords do not match.')
        
        return confirm_password
    
    def clean_new_password(self):
        """Validate new password strength"""
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            # Check if new password is same as current
            if self.user.check_password(new_password):
                raise forms.ValidationError('New password must be different from current password.')
            
            # Basic password strength validation
            if len(new_password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            
            if not any(c.isupper() for c in new_password):
                raise forms.ValidationError('Password must contain at least one uppercase letter.')
            
            if not any(c.islower() for c in new_password):
                raise forms.ValidationError('Password must contain at least one lowercase letter.')
            
            if not any(c.isdigit() for c in new_password):
                raise forms.ValidationError('Password must contain at least one number.')
        
        return new_password
    
    def save(self):
        """Save the new password"""
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        return self.user