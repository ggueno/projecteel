from django import forms
from core.models import Project
from core.models import Offer
from taggit_autosuggest.widgets import TagAutoSuggest


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date', 'like', 'view')
        widgets = {
            'skills': TagAutoSuggest(),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
