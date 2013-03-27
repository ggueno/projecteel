import re

from django import forms
from django.db import models
from django.contrib.auth.models import User
from core.models import Project, Offer, Education, Experience, Comment, Applicant, ApplicantOffer, Profile
from taggit_autosuggest.widgets import TagAutoSuggest
from tinymce.widgets import TinyMCE
import random, string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def make_custom_datefield(f,**kwargs):
    formfield = f.formfield(**kwargs)
    if isinstance(f, models.DateField):
        formfield.widget.input_formats = '%d/%m/%y'
        formfield.widget.attrs.update({'class':'datePicker', 'readonly':'true', 'id': id_generator()})
    return formfield


class ProjectForm(forms.ModelForm):
    as_values_participant = forms.fields.CharField(required=False, widget=forms.TextInput())
    as_values_categories = forms.fields.CharField(required=False, widget=forms.TextInput())

    class Meta:
        model = Project
        exclude = ('slug', 'categories', 'publish_date', 'like', 'view', 'published', 'images', 'owner', 'participant')
        widgets = {
            'skills': TagAutoSuggest(),
            'state': forms.RadioSelect(),
        }

    def clean_as_values_categories(self):
        data = self.cleaned_data
        categories_list = data.get('as_values_categories', None)
        # raise forms.ValidationError('%s does not exist' % self.cleaned_data)
        if categories_list is not None:
            categories_list = categories_list.split(',')

        return categories_list

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
        categories_list = data.get('as_values_categories', None)

        if participant_list is not None:
            for participant_name in participant_list:
                if participant_name.isdigit():
                    participant = Applicant.objects.get(id=int(participant_name))
                    mminstance.participant.add(participant)

        if categories_list is not None:
            for category_name in categories_list:
                Category
                mminstance.categories.add(category_name)


        # mminstance.save()
        return mminstance


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'date_signin', 'cover_image', 'cover_image_top', 'avatar', 'first_visit')


class CoverImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('id','cover_image')

    def __init__(self, *args, **kwargs):
        super(CoverImageForm, self).__init__(*args, **kwargs)
        self.fields['cover_image'].widget.attrs['name'] = "files\[\]"
        self.fields['cover_image'].widget.attrs['data-url'] = "/profile/update_cover/"


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('id','avatar')

    def __init__(self, *args, **kwargs):
        super(AvatarForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs['name'] = "files\[\]"
        self.fields['avatar'].widget.attrs['data-url'] = "/profile/update_avatar/"


class OfferForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    content = forms.CharField(widget=TinyMCE)
    class Meta:
        model = Offer
        exclude = ('slug', 'company')

    def save(self, commit=True):
        data = self.cleaned_data
        content = data.get('content')
        pattern = re.compile(r'<p>&lt;/?[a-z]*/?&gt;</p>')
        content = pattern.sub(r"", content)
        self.instance.content = content
        offerInstance = super(OfferForm, self).save(commit=commit)
        return offerInstance


class EducationForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Education
        exclude = ('owner', 'school_profile')


class ExperienceForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Experience
        exclude = ('owner', 'company_profile')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('profile', 'publish_date', 'project')


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        exclude = ('user', 'educations', 'experiences', 'bookmarks', 'cover_image', 'cover_image_top', 'avatar', 'available', 'first_visit')
        widgets = {
            # 'social_network': forms.TextInput(),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class ApplyForm(forms.ModelForm):
    class Meta:
        model = ApplicantOffer
        exclude = ('applicant', 'publish_date', 'offer')
