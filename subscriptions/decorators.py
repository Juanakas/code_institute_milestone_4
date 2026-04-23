from django.contrib import messages
from functools import wraps
from django.shortcuts import redirect


def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            membership = getattr(request.user, 'membership', None)
            if membership and membership.has_access:
                return view_func(request, *args, **kwargs)
        except Exception:
            pass

        messages.warning(request, 'An active subscription is required to access member content.')
        return redirect('subscriptions:pricing')

    return _wrapped_view
