from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe

from subscriptions.models import Membership, SubscriptionPlan
from django.utils import timezone
from datetime import timedelta


def _get_price_id():
    plan = SubscriptionPlan.objects.filter(is_active=True).order_by('monthly_price').first()
    if plan and plan.stripe_price_id:
        return plan.stripe_price_id
    return getattr(settings, 'STRIPE_SUBSCRIPTION_PRICE_ID', '')


@login_required
@require_POST
def create_checkout_session(request):
    price_id = _get_price_id()
    if not price_id or not settings.STRIPE_SECRET_KEY:
        # Dev fallback: render a simple preview page with a "Complete payment" button
        return render(request, 'checkout/checkout_preview.html', {
            'monthly_price': getattr(settings, 'SUBSCRIPTION_MONTHLY_PRICE', None),
        })

    stripe.api_key = settings.STRIPE_SECRET_KEY
    membership, _ = Membership.objects.get_or_create(user=request.user)
    if membership.has_access:
        messages.info(request, 'Your subscription is already active. Use the status page to manage it.')
        return redirect('subscriptions:status')

    checkout_kwargs = {
        'mode': 'subscription',
        'client_reference_id': str(request.user.id),
        'line_items': [{
            'price': price_id,
            'quantity': 1,
        }],
        'metadata': {
            'user_id': str(request.user.id),
            'username': request.user.username,
        },
        'success_url': request.build_absolute_uri(reverse('checkout:success')) + '?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url': request.build_absolute_uri(reverse('subscriptions:pricing')),
    }
    if membership.stripe_customer_id:
        checkout_kwargs['customer'] = membership.stripe_customer_id
    else:
        checkout_kwargs['customer_email'] = request.user.email

    checkout_session = stripe.checkout.Session.create(**checkout_kwargs)
    return redirect(checkout_session.url, permanent=False)


@login_required
def dev_complete_payment(request):
    # This view handles the dev preview's "Complete payment" action — it simulates a successful subscription.
    membership, _ = Membership.objects.get_or_create(user=request.user)
    membership.status = membership.STATUS_ACTIVE
    membership.current_period_end = timezone.now() + timedelta(days=30)
    membership.save()
    return redirect('checkout:success')


@login_required
def success(request):
    membership = getattr(request.user, 'membership', None)
    # If returning from Stripe Checkout with a session_id, mark membership active for demo/educational mode.
    session_id = request.GET.get('session_id')
    if session_id:
        # Activate membership regardless of actual payment outcome for educational/testing purposes.
        membership, _ = Membership.objects.get_or_create(user=request.user)
        membership.status = membership.STATUS_ACTIVE
        from django.utils import timezone
        from datetime import timedelta
        membership.current_period_end = timezone.now() + timedelta(days=30)
        membership.save()

    return render(request, 'checkout/success.html', {'membership': membership})
