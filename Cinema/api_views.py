from rest_framework import viewsets

from .models import SubscriptionType, Subscription, MovieOrder, Restaurant, Snack, SnackOrder, SubscriptionPayment
from .serializers import (
    SubscriptionTypeSerializer,
    SubscriptionSerializer,
    MovieOrderSerializer,
    RestaurantSerializer,
    SnackSerializer,
    SnackOrderSerializer, SubscriptionPaymentSerializer,
)


class SubscriptionTypeViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionTypeSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class MovieOrderViewSet(viewsets.ModelViewSet):
    queryset = MovieOrder.objects.all()
    serializer_class = MovieOrderSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer


class SnackViewSet(viewsets.ModelViewSet):
    queryset = Snack.objects.all()
    serializer_class = SnackSerializer


class SnackOrderViewSet(viewsets.ModelViewSet):
    queryset = SnackOrder.objects.all()
    serializer_class = SnackOrderSerializer


class SubscriptionPaymentViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer