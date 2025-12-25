def current_user(request):
    return {
        'request_user': request.user if request.user.is_authenticated else None
    }
