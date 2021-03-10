from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import ModelForm

from accounts.models import *


class CreateCourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'created_by']


class AddLessonForm(forms.Form):
    title = forms.CharField(max_length=200)
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv'])])
    content = forms.CharField(max_length=10000)
