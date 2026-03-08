from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ReaderProfile, WriterProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        required=True
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='reader'
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Tell us about yourself and what you\'re interested in...'
        }),
        required=False,
        help_text="Share a bit about yourself and what you're interested in"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'bio')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.bio = self.cleaned_data['bio']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Leave blank to keep current password',
            'class': 'form-control'
        }),
        required=False,
        help_text="Leave blank to keep current password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm new password',
            'class': 'form-control'
        }),
        required=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'bio', 'website', 'twitter', 'linkedin')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Tell us about yourself'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@yourusername'
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your LinkedIn profile'
            }),
        }
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password and len(new_password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return new_password
    
    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match.")
        return confirm_password
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        return user


class ReaderProfileForm(forms.ModelForm):
    favorite_categories = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '["Data Science", "Machine Learning", "Web Development"]'
        }),
        required=False,
        help_text="JSON format: ['Data Science', 'Machine Learning']"
    )
    
    reading_preferences = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '{"preferred_length": "medium", "difficulty": "intermediate"}'
        }),
        required=False,
        help_text="JSON format: {'preferred_length': 'short/medium/long', 'difficulty': 'beginner/intermediate/advanced'}"
    )

    class Meta:
        model = ReaderProfile
        fields = ('favorite_categories', 'reading_preferences')
        widgets = {
            'favorite_categories': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': '["Data Science", "Machine Learning", "Web Development"]'
            }),
            'reading_preferences': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': '{"preferred_length": "medium", "difficulty": "intermediate"}'
            }),
        }


class WriterProfileForm(forms.ModelForm):
    expertise_areas = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': '["Data Science", "Machine Learning", "Python"]'
        }),
        required=False,
        help_text="JSON format: ['Data Science', 'Machine Learning']"
    )

    class Meta:
        model = WriterProfile
        fields = ('expertise_areas',)
        widgets = {
            'expertise_areas': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': '["Data Science", "Machine Learning", "Python"]'
            }),
        }
