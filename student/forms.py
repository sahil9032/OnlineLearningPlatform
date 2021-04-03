from django.core.validators import FileExtensionValidator
from django.forms import forms


class CreateSubmissionForm(forms.Form):
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
