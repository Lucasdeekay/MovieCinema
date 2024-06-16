from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import (
    SubscriptionTypeViewSet,
    SubscriptionViewSet,
    MovieOrderViewSet,
    RestaurantViewSet,
    SnackViewSet,
    SnackOrderViewSet, SubscriptionPaymentViewSet, MovieViewSet, SeatViewSet
)

router = DefaultRouter()
router.register(r'subscriptions/types', SubscriptionTypeViewSet, basename='subscription_type')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'movie', MovieViewSet, basename='movie')
router.register(r'movie-orders', MovieOrderViewSet, basename='movie_order')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'snacks', SnackViewSet, basename='snack')
router.register(r'snack-orders', SnackOrderViewSet, basename='snack_order')
router.register(r'subscription/payments', SubscriptionPaymentViewSet, basename='subscription_payment')
router.register(r'seats', SeatViewSet, basename='seat')


urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_view, name='register'),
    path('forgot-password', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<int:user_id>', views.password_reset_view, name='password_reset'),
    path('profile', views.profile_view, name='profile'),
    path('transaction', views.transaction_view, name='transaction'),
    path('subscription', views.subscription, name='subscription'),
    path('subscription/<str:subscription_name>', views.change_subscription_view, name='change_subscription'),
    path('home', views.movie_rows, name='home'),
    path('get_available_seats', views.get_available_seats, name='get_available_seats'),
    path('movie-detail/<int:movie_id>', views.movie_detail, name='movie_detail'),
    path('verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('api', include(router.urls)),
]
