from accounts.models import User

def logged_user(request):
    user_id = request.session.get('user_id')

    if user_id:
        try:
            return {'request_user': User.objects.get(id=user_id)}
        except User.DoesNotExist:
            pass

    return {'request_user': None}
