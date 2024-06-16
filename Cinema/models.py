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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.subscription_type} - {self.expiry_date}'

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


class Movie(models.Model):
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title


class Restaurant(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Snack(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class SnackOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    snack = models.ForeignKey(Snack, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField(default=timezone.now().date())

    def __str__(self):
        return f'{self.user} - {self.snack}'


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())

    def __str__(self):
        return f'{self.user} - {self.subscription_type} - {self.subscription_type.price}'


class Seat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f'{self.user} - {self.seat_no}'


class MovieOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    snack = models.ForeignKey(SnackOrder, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.movie} - {self.is_valid}'
