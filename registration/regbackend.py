from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.backends.custom.forms import RegistrationForm, UserRegistrationForm
from registration.models import RegistrationProfile

from registration.backends import default



class Backend(default.DefaultBackend):
    def register(self, request, **kwargs):
        email, password, user_category = kwargs['email'], kwargs['password1'], kwargs['user_category']
        username = email
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user