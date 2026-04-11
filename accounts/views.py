from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup(request):
	if request.user.is_authenticated:
		return redirect('videos:member-library')

	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Your account is ready. Log in to open the members library, captions, and practice tools.')
			return redirect('login')
	else:
		form = SignUpForm()

	return render(request, 'accounts/signup.html', {'form': form})
