from __future__ import absolute_import

from django.http import HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from .forms import SocialNetworkForm, InstantMessengerForm, WebsiteForm


@login_required
def elsewhere(request, template_name='elsewhere/elsewhere.html',
    extra_context=None, **kwargs):
    if request.method == 'POST':

        new_data = request.POST.copy()

        # Add forms
        if new_data.get('sn-form') or new_data.get('im-form')\
             or new_data.get('w-form'):

            if new_data.get('sn-form'):
                form = SocialNetworkForm(new_data)
            elif new_data.get('im-form'):
                form = InstantMessengerForm(new_data)
            elif new_data.get('w-form'):
                form = WebsiteForm(new_data)

            if form.is_valid():
                profile = form.save(commit=False)
                profile.object = request.user
                profile.save()
                return HttpResponseRedirect(request.path)

        # Delete forms
        elif new_data.get('delete-sn-form') or new_data.get('delete-im-form')\
             or new_data.get('delete-w-form'):
            delete_id = request.POST['delete_id']

            if new_data.get('delete-sn-form'):
                request.user.social_network_profiles.get(id=delete_id).delete()
            elif new_data.get('delete-im-form'):
                request.user.instant_messenger_profiles.get(id=delete_id).delete()
            elif new_data.get('delete-w-form'):
                request.user.website_profiles.get(id=delete_id).delete()

            return HttpResponseRedirect(request.path)

        # WTF?
        else:
            return HttpResponseServerError

    # Create blank forms
    sn_form = SocialNetworkForm()
    im_form = InstantMessengerForm()
    w_form = WebsiteForm()

    context = {
        'sn_form': sn_form,
        'im_form': im_form,
        'w_form': w_form,
    }

    if extra_context is not None:
        context.update(extra_context)

    return render_to_response(template_name, context,
        context_instance=RequestContext(request))
