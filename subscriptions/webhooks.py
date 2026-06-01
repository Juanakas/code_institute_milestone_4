from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from .webhook_handler import StripeWebhookHandler


@csrf_exempt
@require_POST
def stripe_webhook(request):
	payload = request.body
	signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
	stripe.api_key = settings.STRIPE_SECRET_KEY

	try:
		event = stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
	except ValueError:
		return HttpResponseBadRequest('Invalid payload')
	except stripe.error.SignatureVerificationError:
		return HttpResponseBadRequest('Invalid signature')

	handler = StripeWebhookHandler(event)
	handler.handle_event()
	return HttpResponse(status=200)