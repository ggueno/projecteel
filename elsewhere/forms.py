from __future__ import absolute_import

from django import forms

from .models import SocialNetworkProfile, InstantMessengerProfile, WebsiteProfile


class SocialNetworkForm(forms.ModelForm):
    class Meta:
        model = SocialNetworkProfile
        fields = ('network', 'username')


class InstantMessengerForm(forms.ModelForm):
    class Meta:
        model = InstantMessengerProfile
        fields = ('network', 'username')


class WebsiteForm(forms.ModelForm):
    class Meta:
        model = WebsiteProfile
        fields = ('name', 'url')
