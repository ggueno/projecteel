from django import forms
from core.models import Project
from core.models import Offer, Comment
from taggit_autosuggest.widgets import TagAutoSuggest


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date', 'like', 'view', 'published', 'images', 'owner')
        widgets = {
            'skills': TagAutoSuggest(),
            'participant': forms.TextInput(),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        exclude = ('slug', 'company')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('profile', 'publish_date', 'project')