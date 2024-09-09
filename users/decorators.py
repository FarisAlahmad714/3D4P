from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def verified_member_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            return function(request, *args, **kwargs)
        else:
            return redirect('application_status')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap