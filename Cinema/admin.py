from django.contrib import admin

from .models import SubscriptionType, Subscription, MovieOrder, Restaurant, Snack, SnackOrder, SubscriptionPayment, \
    Movie, Seat


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'is_active')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Snack)
class SnackAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(SnackOrder)
class SnackOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'snack', 'restaurant', 'quantity', 'total_price', 'date')


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'date')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('user', 'seat_no', 'date')


@admin.register(MovieOrder)
class MovieOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'snack', 'seat', 'date', 'is_used')
