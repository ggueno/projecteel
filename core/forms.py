from django import forms
from core.models import Project
from core.models import Offer


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date', 'like', 'view')
        widgets = {
            'skills': forms.TextInput(attrs={'size': '40'}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
