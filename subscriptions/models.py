from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SubscriptionPlan(models.Model):
	name = models.CharField(max_length=100)
	stripe_price_id = models.CharField(max_length=100, unique=True)
	monthly_price = models.DecimalField(max_digits=6, decimal_places=2)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ['monthly_price']

	def __str__(self):
		return f'{self.name} (€{self.monthly_price}/month)'


class Membership(models.Model):
	STATUS_ACTIVE = 'active'
	STATUS_TRIALING = 'trialing'
	STATUS_PAST_DUE = 'past_due'
	STATUS_CANCELED = 'canceled'
	STATUS_INCOMPLETE = 'incomplete'

	STATUS_CHOICES = [
		(STATUS_ACTIVE, 'Active'),
		(STATUS_TRIALING, 'Trialing'),
		(STATUS_PAST_DUE, 'Past Due'),
		(STATUS_CANCELED, 'Canceled'),
		(STATUS_INCOMPLETE, 'Incomplete'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
	stripe_customer_id = models.CharField(max_length=100, blank=True)
	stripe_subscription_id = models.CharField(max_length=100, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INCOMPLETE)
	current_period_end = models.DateTimeField(null=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.user.username} - {self.status}'

	@property
	def has_access(self):
		if self.status not in {self.STATUS_ACTIVE, self.STATUS_TRIALING}:
			return False
		if not self.current_period_end:
			return False
		return self.current_period_end >= timezone.now()

	@property
	def days_remaining(self):
		if not self.current_period_end or not self.has_access:
			return 0
		delta = self.current_period_end.date() - timezone.now().date()
		return max(0, delta.days)
