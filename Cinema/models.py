from django.contrib.auth.models import User
from django.db import models
from datetime import date


class SubscriptionType(models.Model):
    NAME_CHOICES = (
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    name = models.CharField(max_length=10, choices=NAME_CHOICES, primary_key=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    expiry_date = models.DateField(null=True, blank=True)

    def is_active(self):
        if self.expiry_date is None:
            return True  # Free subscription is always active
        return self.expiry_date >= date.today()


class MovieCategory(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5, decimal_places=2)


class Movie(models.Model):
    # Consider using an external movie data ID here (e.g., from Netflix API)
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(MovieCategory, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    payment_completed = models.BooleanField(default=False)
    # Additional fields for order details like timestamp, payment reference, etc.
