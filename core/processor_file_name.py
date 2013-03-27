from models import Profile, User, Follow
from notifications.models import Notification

def user(request):
    try:
        if hasattr(request, 'user'):

            print request.user
            if request.user.id:
                user = User.objects.get(pk=request.user.id)
    		
                myself = Profile.objects.get(user_id=request.user.id)
                following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
                notifications = Notification.objects.filter(actor_object_id__in=following)
            
                return {'myself': user, 
                      'user_avatar': myself.avatar,
                      'unread_notifications': notifications.unread().count
                       }
            return {}
        print "hasnoattr user"
        return {}
    except Profile.DoesNotExist:
        print "hasnoattr user"
        return {}
        
    return {}