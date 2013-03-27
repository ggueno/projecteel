from models import Profile, User, Follow
from notifications.models import Notification

def user(request):
    try:
        if hasattr(request, 'user'):

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
        
        return {}
    except Profile.DoesNotExist:
        
        return {}
        
    return {}