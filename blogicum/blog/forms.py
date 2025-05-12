from django import forms
from .models import Post, Comment
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'category', 'location', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }
