from models import Profile, User

def user(request):
    if hasattr(request, 'user'):

    	if request.user.id:
    		user = User.objects.get(pk=request.user.id)
    		myself =  Profile.objects.get(pk=request.user.id)

	        return {'myself': user, 
	        		'user_avatar': myself.avatar,
	        		'unread_notifications': user.notifications.unread().count
	    			}
		return {}
    return {}