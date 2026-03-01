import datetime
import json

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Membership, SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY


def pricing(request):
	plans = SubscriptionPlan.objects.filter(is_active=True)
	return render(
		request,
		'subscriptions/pricing.html',
		{
			'plans': plans,
			'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
		},
	)


@login_required
def create_checkout_session(request, plan_id):
	plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
	membership = getattr(request.user, 'membership', None)
	if membership is None:
		membership = Membership.objects.create(user=request.user)

	if not settings.STRIPE_SECRET_KEY:
		messages.error(request, 'Stripe is not configured yet. Add Stripe keys to continue.')
		return redirect('subscriptions:pricing')

	try:
		if not membership.stripe_customer_id:
			customer = stripe.Customer.create(
				email=request.user.email,
				metadata={'username': request.user.username},
			)
			membership.stripe_customer_id = customer.id
			membership.save(update_fields=['stripe_customer_id'])

		checkout_session = stripe.checkout.Session.create(
			customer=membership.stripe_customer_id,
			payment_method_types=['card'],
			line_items=[
				{
					'price': plan.stripe_price_id,
					'quantity': 1,
				}
			],
			mode='subscription',
			client_reference_id=request.user.id,
			success_url=request.build_absolute_uri('/subscriptions/success/') + '?session_id={CHECKOUT_SESSION_ID}',
			cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
			metadata={'plan_id': plan.id},
		)
	except stripe.error.StripeError as error:
		messages.error(request, f'Stripe checkout failed: {str(error)}')
		return redirect('subscriptions:pricing')

	return redirect(checkout_session.url, code=303)


@login_required
def subscription_status(request):
	membership = getattr(request.user, 'membership', None)
	return render(request, 'subscriptions/status.html', {'membership': membership})


def checkout_success(request):
	return render(request, 'subscriptions/checkout_success.html')


def checkout_cancel(request):
	return render(request, 'subscriptions/checkout_cancel.html')


@csrf_exempt
def stripe_webhook(request):
	payload = request.body
	sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
	webhook_secret = settings.STRIPE_WEBHOOK_SECRET

	try:
		if webhook_secret:
			event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
		else:
			event = json.loads(payload)
	except (ValueError, stripe.error.SignatureVerificationError):
		return HttpResponse(status=400)

	event_type = event.get('type')
	data_object = event.get('data', {}).get('object', {})

	if event_type == 'checkout.session.completed':
		user_id = data_object.get('client_reference_id')
		customer_id = data_object.get('customer')
		subscription_id = data_object.get('subscription')

		if user_id and subscription_id:
			membership = Membership.objects.filter(user_id=user_id).first()
			if membership:
				try:
					stripe_subscription = stripe.Subscription.retrieve(subscription_id)
				except stripe.error.StripeError:
					return JsonResponse({'received': False, 'detail': 'stripe api error'}, status=400)

				period_end_timestamp = stripe_subscription.get('current_period_end')
				membership.stripe_customer_id = customer_id or membership.stripe_customer_id
				membership.stripe_subscription_id = subscription_id
				membership.status = stripe_subscription.get('status', Membership.STATUS_INCOMPLETE)
				if period_end_timestamp:
					membership.current_period_end = datetime.datetime.fromtimestamp(
						period_end_timestamp,
						tz=datetime.timezone.utc,
					)
				membership.save()

	if event_type in {'customer.subscription.updated', 'customer.subscription.deleted'}:
		subscription_id = data_object.get('id', '')
		customer_id = data_object.get('customer', '')
		membership = Membership.objects.filter(
			stripe_subscription_id=subscription_id,
		).first() or Membership.objects.filter(stripe_customer_id=customer_id).first()

		if membership:
			membership.status = data_object.get('status', Membership.STATUS_CANCELED)
			period_end_timestamp = data_object.get('current_period_end')
			if period_end_timestamp:
				membership.current_period_end = datetime.datetime.fromtimestamp(
					period_end_timestamp,
					tz=datetime.timezone.utc,
				)
			elif membership.status == Membership.STATUS_CANCELED:
				membership.current_period_end = timezone.now()
			membership.save()

	return JsonResponse({'received': True})
