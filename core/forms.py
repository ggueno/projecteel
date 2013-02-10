from django import forms
from core.models import Project, Offer, Education, Experience, Comment, Applicant
from taggit_autosuggest.widgets import TagAutoSuggest


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date', 'like', 'view', 'published', 'images', 'owner')
        widgets = {
            'skills': TagAutoSuggest(),
            'participant': TagAutoSuggest(),
            'state': forms.RadioSelect(),
        }

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        exclude = ('slug', 'company')


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ('owner')
        widgets = {
            'start': forms.DateInput(),
            'end': forms.DateInput(),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ('owner')
        widgets = {
            'start': forms.DateInput(),
            'end': forms.DateInput(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('profile', 'publish_date', 'project')


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        exclude = ('user', 'educations', 'experiences', 'description')
        widgets = {
            'social_network': forms.TextInput(),
        }
