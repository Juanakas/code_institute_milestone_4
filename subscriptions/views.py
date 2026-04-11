import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Membership, SubscriptionPlan


def pricing(request):
	plans = SubscriptionPlan.objects.filter(is_active=True)
	return render(request, 'subscriptions/pricing.html', {'plans': plans})


@login_required
@require_POST
def activate_free_membership(request):
	membership = getattr(request.user, 'membership', None)
	if membership is None:
		membership = Membership.objects.create(user=request.user)

	membership.status = Membership.STATUS_ACTIVE
	membership.current_period_end = timezone.now() + datetime.timedelta(days=30)
	membership.save(update_fields=['status', 'current_period_end', 'updated_at'])

	messages.success(request, 'Your free 30-day membership is now active. Welcome to the member library!')
	return redirect('videos:member-library')


@login_required
def subscription_status(request):
	membership = getattr(request.user, 'membership', None)
	return render(request, 'subscriptions/status.html', {'membership': membership})
