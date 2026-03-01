def membership_status(request):
    has_active_membership = False
    if request.user.is_authenticated:
        membership = getattr(request.user, 'membership', None)
        has_active_membership = bool(membership and membership.has_access)

    return {'has_active_membership': has_active_membership}
