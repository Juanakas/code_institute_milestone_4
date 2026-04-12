import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from subscriptions.models import Membership

from .forms import SignUpForm


def signup(request):
	if request.user.is_authenticated:
		return redirect('videos:member-library')

	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			membership, _ = Membership.objects.get_or_create(user=user)
			membership.status = Membership.STATUS_ACTIVE
			membership.current_period_end = timezone.now() + datetime.timedelta(days=30)
			membership.save(update_fields=['status', 'current_period_end', 'updated_at'])

			messages.success(request, 'Your account is ready and your free 30-day membership is now active. Log in to open the members library.')
			return redirect('login')
	else:
		form = SignUpForm()

	return render(request, 'accounts/signup.html', {'form': form})
