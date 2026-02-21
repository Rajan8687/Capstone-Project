from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ReaderProfile, WriterProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect,
        initial='reader'
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Tell us about yourself"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'bio')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.bio = self.cleaned_data['bio']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'website', 'twitter', 'linkedin')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class ReaderProfileForm(forms.ModelForm):
    favorite_categories = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '["Data Science", "Machine Learning", "Web Development"]'}),
        required=False,
        help_text="JSON format: ['Data Science', 'Machine Learning']"
    )
    
    reading_preferences = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '{"preferred_length": "medium", "difficulty": "intermediate"}'}),
        required=False,
        help_text="JSON format: {'preferred_length': 'short/medium/long', 'difficulty': 'beginner/intermediate/advanced'}"
    )

    class Meta:
        model = ReaderProfile
        fields = ('favorite_categories', 'reading_preferences')


class WriterProfileForm(forms.ModelForm):
    expertise_areas = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '["Data Science", "Machine Learning", "Python"]'}),
        required=False,
        help_text="JSON format: ['Data Science', 'Machine Learning']"
    )

    class Meta:
        model = WriterProfile
        fields = ('expertise_areas',)
