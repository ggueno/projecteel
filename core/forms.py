from django import forms
from core.models import Project


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date')
        widgets = {
            'skills': forms.TextInput(attrs={'size': '40'}),
        }
