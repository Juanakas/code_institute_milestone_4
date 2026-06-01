from django.contrib.auth.models import User
from django.db import models


class CheckoutFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Very difficult'),
        (2, '2 - Difficult'),
        (3, '3 - Neutral'),
        (4, '4 - Easy'),
        (5, '5 - Very easy'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkout_feedback')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comments = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} checkout feedback ({self.rating}/5)'
