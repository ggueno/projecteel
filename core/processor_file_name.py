from models import Profile, User, Follow, Project, Offer, Company
from notifications.models import Notification

def user(request):
    try:
        footer_projects = Project.objects.filter(published=True).order_by('-publish_date')[:3]
        offers = Offer.objects.all().order_by('-publish_date')[:3]
        if hasattr(request, 'user'):

            if request.user.id:
                user = User.objects.get(pk=request.user.id)

                try:
                    myself = Company.objects.get(user_id=user.id)
                    company = True
                except Company.DoesNotExist:
                    company = False
                    myself = Profile.objects.get(user_id=request.user.id)

                following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
                notifications = Notification.objects.filter(actor_object_id__in=following)
                if request.user.id:
                    gueno = True
                else:
                    gueno = False
                print gueno

                return {    'myself': user,
                            'company': company,
                            'myself2' : myself,
                            'user_avatar': myself.avatar,
                            'unread_notifications': notifications.unread().count,
                            'footer_projects' : footer_projects,
                            'offers' : offers,
                            'gueno' : gueno
                       }
            return {}


        return {
            'footer_projects' : footer_projects,
            'offers' : offers
        }
    except Profile.DoesNotExist:

        return {}

    return {}