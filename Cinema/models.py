from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from decimal import Decimal  # Use Decimal for money fields


class SubscriptionType(models.Model):
    NAME_CHOICES = (
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    name = models.CharField(max_length=10, choices=NAME_CHOICES, primary_key=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # Use Decimal('0.00') for clarity


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    expiry_date = models.DateField(null=True, blank=True)

    def is_active(self):
        if self.expiry_date is None:
            return True  # Free subscription is always active
        elif self.expiry_date >= timezone.now().date():
            return True
        else:
            return False

    def add_expiry_date(self):
        """
        Calculates and sets the expiry date based on the provided duration (month or year).
        """
        today = timezone.now().date()
        if self.subscription_type.name == "monthly":
            # Add one month to the current date
            self.expiry_date = today + timezone.timedelta(days=30)  # Adjust for potential month length variations
        elif self.subscription_type.name == "yearly":
            # Add one year to the current date
            self.expiry_date = today + timezone.timedelta(days=365)
        else:
            self.expiry_date = None

        self.save()


class MovieOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)


class Restaurant(models.Model):
    name = models.CharField(max_length=255)


class Snack(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))


class SnackOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    snack = models.ForeignKey(Snack, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    date = models.DateField(default=timezone.now().date())


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())
