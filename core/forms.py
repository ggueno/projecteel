from django import forms
from django.db import models
from core.models import Project, Offer, Education, Experience, Comment, Applicant, ApplicantOffer
from taggit_autosuggest.widgets import TagAutoSuggest


def make_custom_datefield(f):
    formfield = f.formfield()
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
    return formfield

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
    formfield_callback = make_custom_datefield
    class Meta:
        model = Offer
        exclude = ('slug', 'company')


class EducationForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Education
        exclude = ('owner')


class ExperienceForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Experience
        exclude = ('owner')


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


class ApplyForm(forms.ModelForm):
    class Meta:
        model = ApplicantOffer
        exclude = ('applicant', 'publish_date', 'offer')
