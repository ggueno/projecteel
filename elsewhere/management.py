from django.db.models import signals

from elsewhere.default_list import *
from elsewhere.models import SocialNetwork, InstantMessenger

from django.conf import settings


# this function will fill the database with default data (stored in default_lists.py)
def fill_db(sender=None, **kwargs):
    if not kwargs['app'].__name__ == settings.INSTALLED_APPS[-1] + ".models":
        return

    for item in default_social_networks:  # fill social networks
        ident = item.get('identifier', '')

        SocialNetwork.objects.get_or_create(name=item['name'], defaults={
            'url': item['url'],
            'identifier': ident,
            'icon': item['icon']
        })

    for item in default_im_networks:  # fill IM networks
        ident = item.get('identifier', '')

        InstantMessenger.objects.get_or_create(name=item['name'], defaults={
            'url': item['url'],
            'identifier': ident,
            'icon': item['icon']
        })

signals.post_syncdb.connect(fill_db)
