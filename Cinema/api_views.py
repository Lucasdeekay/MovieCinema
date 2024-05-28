from rest_framework import viewsets, permissions
from .models import SubscriptionType, Subscription, MovieCategory, Movie, Order
from .serializers import (
    SubscriptionTypeSerializer, SubscriptionSerializer, MovieCategorySerializer, MovieSerializer, OrderSerializer
)


class SubscriptionTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Subscription Types"""
    permission_classes = [permissions.IsAdminUser]  # Only admins can access
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionTypeSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing user Subscriptions"""
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access
    queryset = Subscription.objects.select_related('subscription_type')  # Pre-fetch subscription type data

    def get_serializer_class(self):
        """
    Override to return the appropriate serializer class based on action (list vs detail)
    """
        if self.action == 'list':
            return SubscriptionSerializer  # Simpler serializer for list view
        else:
            return SubscriptionSerializer  # Full details for detail view (you can customize this further if needed)


class MovieCategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Movie Categories"""
    permission_classes = [permissions.IsAdminUser]  # Only admins can access
    queryset = MovieCategory.objects.all()
    serializer_class = MovieCategorySerializer


class MovieViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Movies"""
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access
    queryset = Movie.objects.select_related('category')  # Pre-fetch category data

    def get_serializer_class(self):
        """
    Override to return the appropriate serializer class based on action (list vs detail)
    """
        if self.action == 'list':
            return MovieSerializer  # Simpler serializer for list view
        else:
            return MovieSerializer  # Full details for detail view (you can customize this further if needed)


class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint for managing user Orders"""
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access
    queryset = Order.objects.select_related('user', 'movie__category')  # Pre-fetch user and movie category data
    serializer_class = OrderSerializer
