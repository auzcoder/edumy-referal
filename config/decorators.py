from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def verified_required(view_func):
    """
    Custom decorator to ensure the user is logged in and verified.
    If not verified, redirects to the waiting page.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_verified:
            # Redirect to the waiting page if the user is not verified
            return redirect('waiting')  # Replace 'waiting' with the correct name of your waiting view
        return view_func(request, *args, **kwargs)

    return _wrapped_view
