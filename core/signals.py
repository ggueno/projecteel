# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from notifications import notify
from core.models import *

def has_follow(sender, instance, created, **kwargs):
    # notify.send(instance.follower.user, recipient=instance.follower.user, verb='has followed you.')
    notify.send(instance.follower,
    			recipient=instance.follower.user,
    			verb=u'suit désormais',
            	action_object=instance,
            	target=instance.following)

post_save.connect(has_follow, sender=Follow)


def like_project(sender, instance, created, **kwargs):
    notify.send(instance.profile,
			recipient=instance.project.owner.user,
			verb=u'a liké',
        	action_object=instance.project)

post_save.connect(like_project, sender=Like)


def comment_project(sender, instance, created, **kwargs):
    notify.send(instance.profile,
			recipient=instance.project.owner.user,
			verb=u'a commenté ',
        	action_object=instance.project)

post_save.connect(comment_project, sender=Comment)

def add_project(sender, instance, created, **kwargs):
	if instance.published == True:
	    notify.send(instance.owner,
	    		recipient=instance.owner.user,
				verb=u'vient d\'ajouter',
	        	action_object=instance)

post_save.connect(add_project, sender=Project)

