from rest_framework import serializers
from .models import SubscriptionType, Subscription, MovieCategory, Movie, Order


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'  # Include all fields


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)  # Show user details as read-only
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('user', 'subscription_type', 'is_active')

    def get_is_active(self, obj):
        return obj.is_active()  # Call the is_active method from the Subscription model


class MovieCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCategory
        fields = '__all__'  # Include all fields


class MovieSerializer(serializers.ModelSerializer):
    category = MovieCategorySerializer(read_only=True)  # Nested serializer for category

    class Meta:
        model = Movie
        fields = ('external_id', 'title', 'category')  # Include relevant movie details


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)  # Show user details as read-only
    movie = MovieSerializer(read_only=True)  # Nested serializer for movie

    class Meta:
        model = Order
        fields = ('user', 'movie', 'payment_completed')
