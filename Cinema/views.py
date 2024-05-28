from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from Cinema.models import Subscription, SubscriptionType, Movie, Order, MovieCategory


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to successful login page
            return redirect('home')  # Replace 'home' with your desired redirect URL
        else:
            # Invalid login credentials
            error_message = 'Invalid username or password.'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            error_message = 'Passwords do not match.'
            return render(request, 'register.html', {'error_message': error_message})
        # Create user
        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                        password=password1)
        user.save()
        # Login the user after successful registration (optional)
        login(request, user)
        return redirect('home')  # Replace 'home' with your desired redirect URL
    return render(request, 'register.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            # Construct reset password URL with the user ID and token
            reset_password_url = f"http://your_domain/reset-password/{user.id}"
            # Send email with reset password link
            send_mail(
                subject='Password Reset Link',
                message=f'Click the link below to reset your password:\n{reset_password_url}',
                from_email='your_email@example.com',  # Replace with your email address
                recipient_list=[email],
            )
            success_message = 'We sent you an email with instructions to reset your password.'
            return render(request, 'forgot_password.html', {'success_message': success_message})
        except User.DoesNotExist:
            error_message = 'Email address not found.'
            return render(request, 'forgot_password.html', {'error_message': error_message})
    return render(request, 'forgot_password.html')


def password_reset_view(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        error_message = 'Invalid user ID.'
        return render(request, 'password_reset.html', {'error_message': error_message})

    if request.method == 'POST':
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']
        if new_password1 != new_password2:
            error_message = 'Passwords do not match.'
            return render(request, 'password_reset.html', {'error_message': error_message})
        # Set the new password
        user.set_password(new_password1)
        user.save()
        # Login the user after successful password reset (optional)
        login(request, user)
        success_message = 'Password reset successfully!'
        return render(request, 'password_reset.html', {'success_message': success_message})
    return render(request, 'password_reset.html')


@login_required
def dashboard_view(request):
    user = request.user
    subscription = Subscription.objects.filter(user=user).first()  # Get user's subscription

    context = {
        'user': user,
        'subscription': subscription,
    }
    return render(request, 'dashboard.html', context)


@login_required
def settings_view(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        user = authenticate(request, username=request.user.username, password=current_password)
        if user is not None:
            if new_password1 != new_password2:
                error_message = 'New passwords do not match.'
            else:
                user.set_password(new_password1)
                user.save()
                success_message = 'Password changed successfully!'
                return render(request, 'settings.html', context={'success_message': success_message})
        else:
            error_message = 'Invalid current password.'
    else:
        error_message = ''  # Clear any previous error messages

    context = {'error_message': error_message}
    return render(request, 'settings.html', context)


@login_required
def change_subscription_view(request):
    if request.method == 'POST':
        selected_type_id = request.POST['subscription_type']
        try:
            selected_type = SubscriptionType.objects.get(pk=selected_type_id)
            user_subscription = request.user.subscription  # Assuming user has a subscription
            user_subscription.subscription_type = selected_type
            user_subscription.save()
            return redirect('payment_success')  # Redirect to payment success page (replace with your URL)
        except SubscriptionType.DoesNotExist:
            error_message = 'Invalid subscription type selected.'
    else:
        subscription_types = SubscriptionType.objects.all()
        error_message = ''  # Clear any previous error messages

    context = {'subscription_types': subscription_types, 'error_message': error_message}
    return render(request, 'change_subscription.html', context)


@login_required
def movie_detail_view(request, title, category):

    movie_category = MovieCategory.objects.get(name=category)

    movie = Movie.objects.create(title=title, category=movie_category)

    # Create an order for the user (assuming immediate purchase)
    order = Order.objects.create(user=request.user, movie=movie)

    context = {'movie': movie, 'order': order}
    return render(request, 'movie_detail.html', context)
