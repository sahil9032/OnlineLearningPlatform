from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    CHOICES = [('student', 'Student'), ('teacher', 'Teacher')]
    role = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
