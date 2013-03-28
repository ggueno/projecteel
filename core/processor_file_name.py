from models import Profile, User, Follow, Project, Offer
from notifications.models import Notification

def user(request):
    try:
        footer_projects = Project.objects.filter(published=True).order_by('-publish_date')[:3]
        offers = Offer.objects.all().order_by('-publish_date')[:3]
        if hasattr(request, 'user'):

            if request.user.id:
                user = User.objects.get(pk=request.user.id)

                myself = Profile.objects.get(user_id=request.user.id)
                following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
                notifications = Notification.objects.filter(actor_object_id__in=following)

                return {    'myself': user,
                            'user_avatar': myself.avatar,
                            'unread_notifications': notifications.unread().count,
                            'footer_projects' : footer_projects,
                            'offers' : offers
                       }
            return {}


        return {
            'footer_projects' : footer_projects,
            'offers' : offers
        }
    except Profile.DoesNotExist:

        return {}

    return {}