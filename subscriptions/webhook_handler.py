from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

import stripe

from .models import Membership


class StripeWebhookHandler:
	def __init__(self, event):
		self.event = event
		self.event_type = event['type']
		self.event_object = event['data']['object']

	def handle_event(self):
		handler_name = self.event_type.replace('.', '_')
		handler = getattr(self, handler_name, None)
		if handler is not None:
			return handler()
		return None

	def checkout_session_completed(self):
		session = self.event_object
		subscription_id = session.get('subscription')
		if not subscription_id:
			return None

		subscription = stripe.Subscription.retrieve(subscription_id)
		membership = self._get_membership(session, subscription)
		if membership is None:
			return None
		self._sync_membership(membership, subscription)
		return membership

	def customer_subscription_updated(self):
		subscription = self.event_object
		membership = self._get_membership_from_subscription(subscription)
		if membership is None:
			return None
		self._sync_membership(membership, subscription)
		return membership

	def customer_subscription_deleted(self):
		subscription = self.event_object
		membership = self._get_membership_from_subscription(subscription)
		if membership is None:
			return None
		self._sync_membership(membership, subscription, status=Membership.STATUS_CANCELED)
		return membership

	def invoice_payment_failed(self):
		invoice = self.event_object
		membership = self._get_membership_from_invoice(invoice)
		if membership is None:
			return None
		membership.status = Membership.STATUS_PAST_DUE
		membership.save(update_fields=['status', 'updated_at'])
		return membership

	def _get_user(self, session=None, subscription=None):
		if session is not None:
			user_id = session.get('client_reference_id') or session.get('metadata', {}).get('user_id')
			if user_id:
				return User.objects.filter(id=user_id).first()

		if subscription is not None:
			metadata = getattr(subscription, 'metadata', {}) or {}
			user_id = metadata.get('user_id')
			if user_id:
				return User.objects.filter(id=user_id).first()

		if session is not None:
			email = session.get('customer_email')
			if email:
				return User.objects.filter(email__iexact=email).first()
		return None

	def _get_membership(self, session, subscription):
		user = self._get_user(session=session, subscription=subscription)
		if user is None:
			return None
		membership, _ = Membership.objects.get_or_create(user=user)
		return membership

	def _get_membership_from_subscription(self, subscription):
		subscription_id = subscription.get('id')
		customer_id = subscription.get('customer')
		membership = Membership.objects.filter(stripe_subscription_id=subscription_id).first()
		if membership is not None:
			return membership
		return Membership.objects.filter(stripe_customer_id=customer_id).first()

	def _get_membership_from_invoice(self, invoice):
		subscription_id = invoice.get('subscription')
		customer_id = invoice.get('customer')
		membership = Membership.objects.filter(stripe_subscription_id=subscription_id).first()
		if membership is not None:
			return membership
		return Membership.objects.filter(stripe_customer_id=customer_id).first()

	def _sync_membership(self, membership, subscription, status=None):
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
		membership.status = status or subscription.get('status', Membership.STATUS_INCOMPLETE)
		membership.cancel_at_period_end = subscription.get('cancel_at_period_end', False)
		membership.current_period_end = period_end
		membership.save(update_fields=['stripe_customer_id', 'stripe_subscription_id', 'stripe_price_id', 'status', 'cancel_at_period_end', 'current_period_end', 'updated_at'])