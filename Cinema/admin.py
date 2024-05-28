from django.contrib import admin
from .models import SubscriptionType, Subscription, MovieCategory, Movie, Order


# Register SubscriptionType model
@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


# Register Subscription model
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'is_active')


# Register MovieCategory model
@admin.register(MovieCategory)
class MovieCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


# Register Movie model (consider adding 'category' to list_display if needed)
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'external_id')  # You can adjust this based on your needs


# Register Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'payment_completed')
