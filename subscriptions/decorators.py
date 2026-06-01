from django.contrib import messages
from functools import wraps
from django.shortcuts import redirect

from .models import Membership


def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        membership = Membership.objects.filter(user_id=request.user.id).first()
        if membership and membership.has_access:
            return view_func(request, *args, **kwargs)

        messages.warning(request, 'An active monthly subscription is required to access member content.')
        return redirect('subscriptions:pricing')

    return _wrapped_view
