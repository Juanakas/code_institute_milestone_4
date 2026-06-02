from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

import stripe

from subscriptions.models import Membership, SubscriptionPlan
from django.utils import timezone
from datetime import datetime, timedelta

from .forms import CheckoutFeedbackForm, CheckoutPreviewForm


def _get_price_id():
    plan = SubscriptionPlan.objects.filter(is_active=True).order_by('monthly_price').first()
    if plan and plan.stripe_price_id:
        return plan.stripe_price_id
    return getattr(settings, 'STRIPE_SUBSCRIPTION_PRICE_ID', '')


def _sync_membership_from_subscription(membership, subscription):
    period_end_value = subscription.get('current_period_end')
    period_end = datetime.fromtimestamp(period_end_value, tz=timezone.get_current_timezone()) if period_end_value else None
    price_id = ''
    items = subscription.get('items')
    if items and items.get('data'):
        price = items['data'][0].get('price', {})
        price_id = price.get('id', '')

    membership.stripe_customer_id = subscription.get('customer', '')
    membership.stripe_subscription_id = subscription.get('id', '')
    membership.stripe_price_id = price_id
    membership.status = subscription.get('status', Membership.STATUS_INCOMPLETE)
    membership.cancel_at_period_end = subscription.get('cancel_at_period_end', False)
    membership.current_period_end = period_end
    membership.save(update_fields=['stripe_customer_id', 'stripe_subscription_id', 'stripe_price_id', 'status', 'cancel_at_period_end', 'current_period_end', 'updated_at'])


def _activate_membership_from_checkout_session(request):
    session_id = request.GET.get('session_id', '').strip()
    if not session_id or not settings.STRIPE_SECRET_KEY:
        return False

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return False

    session_user_id = str(session.get('client_reference_id') or session.get('metadata', {}).get('user_id') or '')
    if session_user_id and session_user_id != str(request.user.id):
        return False

    payment_status = (session.get('payment_status') or '').lower()
    if payment_status not in {'paid', 'no_payment_required'}:
        return False

    if session.get('mode') != 'subscription':
        return False

    subscription_id = session.get('subscription')
    if not subscription_id:
        return False

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
    except stripe.error.StripeError:
        return False

    membership, _ = Membership.objects.get_or_create(user=request.user)
    _sync_membership_from_subscription(membership, subscription)
    return membership.has_access


@login_required
@require_POST
def create_checkout_session(request):
    price_id = _get_price_id()
    if not price_id or not settings.STRIPE_SECRET_KEY:
        if not settings.DEBUG:
            messages.error(request, 'Checkout is temporarily unavailable. Please try again shortly.')
            return redirect('subscriptions:pricing')

        # Dev fallback: render an academic checkout form with realistic required inputs.
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
        form = CheckoutPreviewForm(initial=initial_data)
        return render(request, 'checkout/checkout_preview.html', {
            'monthly_price': getattr(settings, 'SUBSCRIPTION_MONTHLY_PRICE', None),
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
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
@require_POST
def dev_complete_payment(request):
    if not settings.DEBUG:
        return redirect('subscriptions:pricing')

    form = CheckoutPreviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please complete all required payment details to continue.')
        return render(request, 'checkout/checkout_preview.html', {
            'monthly_price': getattr(settings, 'SUBSCRIPTION_MONTHLY_PRICE', None),
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }, status=400)

    # This view handles the dev preview's "Complete payment" action — it simulates a successful subscription.
    membership, _ = Membership.objects.get_or_create(user=request.user)
    membership.status = membership.STATUS_ACTIVE
    membership.current_period_end = timezone.now() + timedelta(days=30)
    membership.save()
    messages.success(request, 'Membership activated successfully. Welcome to the members area.', extra_tags='popup')
    return redirect('videos:member-library')


@login_required
def success(request):
    _activate_membership_from_checkout_session(request)
    membership, _ = Membership.objects.get_or_create(user=request.user)

    if request.method == 'GET' and membership.has_access and request.GET.get('session_id'):
        messages.success(request, 'Payment successful. Your members area is now unlocked.', extra_tags='popup')
        return redirect('videos:member-library')

    # Subscription activation in production is handled by Stripe webhooks.
    # This view also verifies Stripe Checkout return session_id as a fallback.
    # In debug mode without Stripe credentials, dev_complete_payment handles activation.

    feedback_form = CheckoutFeedbackForm()
    if request.method == 'POST':
        if not membership or not membership.has_access:
            messages.error(request, 'You can submit checkout feedback after your subscription is active.')
            return redirect('checkout:success')

        feedback_form = CheckoutFeedbackForm(request.POST)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thanks for your checkout feedback.')
            return redirect('checkout:success')

    recent_feedback = request.user.checkout_feedback.all()[:3]

    return render(request, 'checkout/success.html', {
        'membership': membership,
        'feedback_form': feedback_form,
        'recent_feedback': recent_feedback,
    })
