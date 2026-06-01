from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from subscriptions.models import Membership

from .forms import SignUpForm


class MemberLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return '/admin/'
        membership = Membership.objects.filter(user_id=self.request.user.id).first()
        if membership and membership.has_access:
            return reverse('videos:member-library')
        return reverse('subscriptions:pricing')


def signup(request):
    if request.user.is_authenticated:
        return redirect('videos:member-library')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account is ready. Choose the monthly subscription to unlock the members library.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})
