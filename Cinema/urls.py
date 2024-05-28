from django.urls import path, include
from rest_framework import routers

from . import views
from .api_views import (
    SubscriptionTypeViewSet, SubscriptionViewSet, MovieCategoryViewSet, MovieViewSet, OrderViewSet
)

router = routers.DefaultRouter()
router.register('subscriptions/types', SubscriptionTypeViewSet)  # Base URL for subscription types
router.register('subscriptions', SubscriptionViewSet)  # Base URL for user subscriptions
router.register('categories', MovieCategoryViewSet)  # Base URL for movie categories
router.register('movies', MovieViewSet)  # Base URL for movies
router.register('orders', OrderViewSet)  # Base URL for user orders

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<int:user_id>/<str:token>/', views.password_reset_view, name='password_reset'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('subscription/', views.change_subscription_view, name='subscription'),
    path('movie-detail/', views.movie_detail_view, name='movie_detail'),
    path('api', include(router.urls)),
]
