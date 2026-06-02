from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Membership, SubscriptionPlan


def _sync_membership_from_subscription(membership, subscription):
    period_end_value = subscription.get('current_period_end')
    fallback_period_end = timezone.now() + timedelta(days=30)
    period_end = datetime.fromtimestamp(period_end_value, tz=timezone.get_current_timezone()) if period_end_value else fallback_period_end
    if period_end < fallback_period_end:
        period_end = fallback_period_end

    price_id = ''
    items = subscription.get('items')
    if items and items.get('data'):
        price = items['data'][0].get('price', {})
        price_id = price.get('id', '')

    membership.stripe_customer_id = subscription.get('customer', '')
    membership.stripe_subscription_id = subscription.get('id', '')
    membership.stripe_price_id = price_id
    membership.status = subscription.get('status', Membership.STATUS_ACTIVE)
    membership.cancel_at_period_end = subscription.get('cancel_at_period_end', False)
    membership.current_period_end = period_end
    membership.save(update_fields=['stripe_customer_id', 'stripe_subscription_id', 'stripe_price_id', 'status', 'cancel_at_period_end', 'current_period_end', 'updated_at'])


def _activate_membership_from_session(request):
    session_id = request.GET.get('session_id', '').strip()
    if not session_id or not settings.STRIPE_SECRET_KEY:
        return None

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return None

    session_user_id = str(session.get('client_reference_id') or session.get('metadata', {}).get('user_id') or '')
    if session_user_id and session_user_id != str(request.user.id):
        return None

    payment_status = (session.get('payment_status') or '').lower()
    if payment_status not in {'paid', 'no_payment_required'}:
        return None

    if session.get('mode') != 'subscription':
        return None

    subscription_id = session.get('subscription')
    if not subscription_id:
        return None

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
    except stripe.error.StripeError:
        return None

    membership, _ = Membership.objects.get_or_create(user=request.user)
    _sync_membership_from_subscription(membership, subscription)
    return membership


def _subscription_display_data():
    plan = SubscriptionPlan.objects.filter(is_active=True).order_by('monthly_price').first()
    if plan is not None:
        return {
            'plan': plan,
            'name': plan.name,
            'monthly_price': plan.monthly_price,
            'stripe_price_id': plan.stripe_price_id or settings.STRIPE_SUBSCRIPTION_PRICE_ID,
        }

    return {
        'plan': None,
        'name': settings.SUBSCRIPTION_NAME,
        'monthly_price': settings.SUBSCRIPTION_MONTHLY_PRICE,
        'stripe_price_id': settings.STRIPE_SUBSCRIPTION_PRICE_ID,
    }


def pricing(request):
    context = _subscription_display_data()
    context['membership'] = getattr(request.user, 'membership', None) if request.user.is_authenticated else None
    return render(request, 'subscriptions/pricing.html', context)


@login_required
@require_POST
def create_checkout_session(request):
    context = _subscription_display_data()
    price_id = context['stripe_price_id']
    if not price_id:
        messages.error(request, 'Stripe is not configured yet. Add a subscription price ID and try again.')
        return redirect('subscriptions:pricing')

    membership, _ = Membership.objects.get_or_create(user=request.user)
    if membership.has_access:
        messages.info(request, 'Your subscription is already active. Use the status page to manage it.')
        return redirect('subscriptions:status')

    stripe.api_key = settings.STRIPE_SECRET_KEY
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
        'success_url': (
            request.build_absolute_uri(reverse('subscriptions:subscription_success'))
            + '?session_id={CHECKOUT_SESSION_ID}'
        ),
        'cancel_url': request.build_absolute_uri(reverse('subscriptions:pricing')),
    }
    if membership.stripe_customer_id:
        checkout_kwargs['customer'] = membership.stripe_customer_id
    else:
        checkout_kwargs['customer_email'] = request.user.email

    checkout_session = stripe.checkout.Session.create(**checkout_kwargs)
    return redirect(checkout_session.url, permanent=False)


@login_required
def subscription_success(request):
    membership = _activate_membership_from_session(request)
    if membership and membership.has_access:
        messages.success(request, 'Payment successful. Your members area is now unlocked.', extra_tags='popup')
        return redirect('videos:member-library')

    context = _subscription_display_data()
    context['membership'] = getattr(request.user, 'membership', None)
    return render(request, 'subscriptions/success.html', context)


@login_required
def subscription_status(request):
    membership = getattr(request.user, 'membership', None)
    if membership and membership.status in {Membership.STATUS_ACTIVE, Membership.STATUS_TRIALING} and not membership.current_period_end:
        membership.current_period_end = timezone.now() + timedelta(days=30)
        membership.save(update_fields=['current_period_end', 'updated_at'])

    context = _subscription_display_data()
    context['membership'] = getattr(request.user, 'membership', None)
    return render(request, 'subscriptions/status.html', context)


@login_required
@require_POST
def manage_subscription(request):
    membership = getattr(request.user, 'membership', None)
    if not membership or not membership.stripe_customer_id:
        messages.error(request, 'No Stripe customer record was found for your account yet.')
        return redirect('subscriptions:status')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    portal_session = stripe.billing_portal.Session.create(
        customer=membership.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse('subscriptions:status')),
    )
    return redirect(portal_session.url, permanent=False)
