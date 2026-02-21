from django import forms
from .models import Article, Category, Tag, Comment


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'tags', 'content', 'excerpt', 'featured_image', 'status', 'is_featured', 'is_trending', 'reading_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter article title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'tag-checkbox-list'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_trending': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reading_time': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 60}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        
        # Add proper CSS classes for dark mode
        self.fields['title'].widget.attrs.update({'placeholder': 'Enter an engaging title for your article'})
        self.fields['content'].widget.attrs.update({'placeholder': 'Write your article content here...'})
        self.fields['excerpt'].widget.attrs.update({'placeholder': 'Brief description of your article (optional)'})
        self.fields['reading_time'].widget.attrs.update({'placeholder': 'Estimated reading time in minutes'})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            }),
        }


class ArticleSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles...'
        })
    )
