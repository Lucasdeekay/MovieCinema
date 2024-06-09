from rest_framework import serializers

from .models import SubscriptionType, Subscription, MovieOrder, Restaurant, Snack, SnackOrder, SubscriptionPayment


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'subscription_type', 'is_active')


class MovieOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieOrder
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class SnackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snack
        fields = '__all__'


class SnackOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnackOrder
        fields = '__all__'


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = '__all__'
