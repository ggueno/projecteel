from django import forms
from django.db import models
from core.models import Project, Offer, Education, Experience, Comment, Applicant, ApplicantOffer
from taggit_autosuggest.widgets import TagAutoSuggest


def make_custom_datefield(f):
    formfield = f.formfield()
    if isinstance(f, models.DateField):
        formfield.widget.input_formats = '%d/%m/%y'
        formfield.widget.attrs.update({'class':'datePicker', 'readonly':'true'})
    return formfield


class ProjectForm(forms.ModelForm):
    as_values_participant = forms.fields.CharField(required=False, widget=forms.TextInput())

    class Meta:
        model = Project
        exclude = ('slug', 'publish_date', 'like', 'view', 'published', 'images', 'owner', 'participant')
        widgets = {
            'skills': TagAutoSuggest(),
            'state': forms.RadioSelect(),
        }

    def clean_as_values_participant(self):
        data = self.cleaned_data
        participant_list = data.get('as_values_participant', None)
        # raise forms.ValidationError('%s does not exist' % self.cleaned_data)
        if participant_list is not None:
            participant_list = participant_list.split(',')
            for participant_name in participant_list:
                participant_id = participant_name
                if participant_name.isdigit():
                    try:
                        participant = Applicant.objects.get(id=int(participant_id))
                    except Applicant.DoesNotExist:
                        raise forms.ValidationError('Applicant %s does not exist' % participant_name)
        return participant_list

    def save(self, commit=True):
        mminstance = super(ProjectForm, self).save(commit=commit)
        data = self.cleaned_data
        participant_list = data.get('as_values_participant', None)
        if participant_list is not None:
            for participant_name in participant_list:
                if participant_name.isdigit():
                    participant = Applicant.objects.get(id=int(participant_name))
                    mminstance.participant.add(participant)

        # mminstance.save()
        return mminstance



class OfferForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Offer
        exclude = ('slug', 'company')


class EducationForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Education

        # school.widgets = forms.TextInput()
        
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
