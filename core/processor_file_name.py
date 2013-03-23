from models import Profile, User

def user(request):
    if hasattr(request, 'user'):

    	user = User.objects.get(pk=request.user.id)
    	myself =  Profile.objects.get(pk=request.user.id)

        return {'myself': user, 
        		'user_avatar': myself.avatar,
        		'unread_notifications': user.notifications.unread().count
    			}
    return {}