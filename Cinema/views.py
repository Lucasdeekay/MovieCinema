import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from paystackapi.transaction import Transaction

from Cinema.models import Subscription, SubscriptionType, MovieOrder, Snack, Restaurant, SnackOrder, SubscriptionPayment

# Import libraries for API requests and YouTube trailer lookup (replace with your preferred methods)
import requests
from youtubesearchpython import VideosSearch

# Replace with your actual TMDB API key
API_KEY = ''
base_url = "https://image.tmdb.org/t/p/original"


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            subscript = Subscription.objects.get(user=user)
            if not subscript.is_active():
                subscript.subscription_type = SubscriptionType.objects.get(name='free')
                subscript.add_expiry_date()
                subscript.save()
            # Redirect to successful login page
            return redirect('home')  # Replace 'home' with your desired redirect URL
        else:
            # Invalid login credentials
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
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
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        # Create user
        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,
                                        password=password1)
        user.save()
        subscription_type = SubscriptionType.objects.get(name='free')
        Subscription.objects.get_or_create(user=user, subscription_type=subscription_type)
        messages.success(request, 'Your account has been successfully created.')
        return redirect('login')  # Replace 'home' with your desired redirect URL
    return render(request, 'register.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            return redirect('password_reset', args=(user.id,))
        except User.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'forgot_password.html')
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
            messages.error(request, 'Passwords do not match.')
            return render(request, 'password_reset.html')
        # Set the new password
        user.set_password(new_password1)
        user.save()
        messages.success(request, 'Password reset successfully!')
        return render(request, 'password_reset.html')
    return render(request, 'password_reset.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    subscript = Subscription.objects.get(user=user)

    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        user = authenticate(request, username=request.user.username, password=current_password)
        if user is not None:
            if new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            else:
                user.set_password(new_password1)
                user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
        else:
            messages.error(request, 'Invalid current password.')
            return redirect('profile')

    context = {
        'user': user,
        'subscription': subscript.subscription_type,
    }
    return render(request, 'profile.html', context)


@login_required
def subscription(request):
    subscript = Subscription.objects.get(user=request.user)

    return render(request, 'subscription.html', {'subscription': subscript.subscription_type})


@login_required
def change_subscription_view(request, subscription_name):
    try:
        selected_type = SubscriptionType.objects.get(name=subscription_name)

        if selected_type.name != 'free':
            response = Transaction.initialize(
                reference=str(uuid.uuid4()),
                amount=float(selected_type.price) * 100,
                email=request.user.email
            )

            user_subscription = Subscription.objects.get(user=request.user)
            user_subscription.subscription_type = selected_type
            user_subscription.add_expiry_date()
            user_subscription.save()

            SubscriptionPayment.objects.create(user=request.user, subscription_type=selected_type)
            messages.success(request, 'Subscription update successful.')
            return HttpResponseRedirect(response['data']['authorization_url'])
        else:
            user_subscription = Subscription.objects.get(user=request.user)
            user_subscription.subscription_type = selected_type
            user_subscription.add_expiry_date()
            user_subscription.save()
            messages.success(request, 'Subscription update successful.')
            return redirect('subscription')
    except SubscriptionType.DoesNotExist:
        messages.error(request, 'Invalid subscription type selected.')
        return redirect('subscription')


@login_required
def movie_rows(request):
    """
  Fetches data for movie rows and handles trailer lookup.

  Renders a template with movie data and potential trailer URLs.
  """
    selected_type = Subscription.objects.get(user=request.user).subscription_type

    if selected_type.name != 'free':
        fetch_urls = {
            'trending': f'/trending/all/week?api_key={API_KEY}&language=en-US',
            'netflix_originals': f'/discover/tv?api_key={API_KEY}&with_networks=213',
            'top_rated': f'/movie/top_rated?api_key={API_KEY}&language=en-US',
            'top_action': f'/discover/movie?api_key={API_KEY}&with_genres=28',
            # 'top_comedy': f'/discover/movie?api_key={API_KEY}&with_genres=35',
            # 'top_horror': f'/discover/movie?api_KEY={API_KEY}&with_genres=27',
            # 'top_romance': f'/discover/movie?api_KEY={API_KEY}&with_genres=10749',
            # 'top_documentaries': f'/discover/movie?api_KEY={API_KEY}&with_genres=99',
        }

        movie_data = {}
        for category, url in fetch_urls.items():
            movies = []
            try:
                response = requests.get(f'https://api.themoviedb.org/3{url}')
                response.raise_for_status()  # Raise an exception for failed requests
                movies = response.json()['results']
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {category}: {e}")

            movie_data[category] = {
                'movies': movies,
            }
        context = {
            'trending': movie_data['trending']['movies'],
            'netflix_originals': movie_data['netflix_originals']['movies'],
            'top_rated': movie_data['top_rated']['movies'],
            'top_action': movie_data['top_action']['movies'],
            'base_url': base_url,
        }

    else:
        fetch_urls = {
            'trending': f'/trending/all/week?api_key={API_KEY}&language=en-US',
        }

        movie_data = {}
        for category, url in fetch_urls.items():
            movies = []
            try:
                response = requests.get(f'https://api.themoviedb.org/3{url}')
                response.raise_for_status()  # Raise an exception for failed requests
                movies = response.json()['results']
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {category}: {e}")

            movie_data[category] = {
                'movies': movies,
            }

        context = {
            'trending': movie_data['trending']['movies'],
            'base_url': base_url,
        }
    return render(request, 'home.html', context)


@login_required
def movie_detail(request, movie_id):
    """
  Fetches details for a specific movie using its ID.

  Renders a template with the movie details.
  """

    user = request.user

    # Handle form submission
    if request.method == 'POST':
        snack_id = request.POST['snack']
        restaurant_id = request.POST['restaurant']
        quantity = request.POST['quantity']

        restaurant = Restaurant.objects.get(id=restaurant_id)
        snack = Snack.objects.get(id=snack_id)

        total_price = float(snack.price) * int(quantity)

        response = Transaction.initialize(
            reference=str(uuid.uuid4()),
            amount=total_price * 100,
            email=user.email
        )

        if response['status']:
            SnackOrder.objects.create(
                user=user,
                snack=snack,
                restaurant=restaurant,
                quantity=int(quantity),
                total_price=total_price
            )

            messages.success(request, f"Order successfully made.")
            return HttpResponseRedirect(response['data']['authorization_url'])

        # Redirect to confirmation or payment page (replace with your logic)
        return redirect('order_confirmation')

    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for failed requests
        movie_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching movie details for ID {movie_id}: {e}")
        return redirect('login')

    MovieOrder.objects.get_or_create(user=user, external_id=movie_id, title=movie_data['original_title'])

    # Available snacks and restaurants
    snacks = Snack.objects.all()
    restaurants = Restaurant.objects.all()

    videosSearch = VideosSearch('NoCopyrightSounds', limit=1)
    results = videosSearch.result()
    trailer_search = results['result']
    trailer_url = trailer_search[0]['link']

    context = {
        'movie': movie_data,
        'movie_title': movie_data['original_title'],
        'vote_average': movie_data['vote_average'],
        'genres': movie_data['genres'],
        'release_date': movie_data['release_date'],
        'backdrop_path': movie_data['backdrop_path'],
        'overview': movie_data['overview'],
        'trailer_url': trailer_url,
        'snacks': snacks,
        'restaurants': restaurants,
        'base_url': base_url,
    }
    return render(request, 'movie_detail.html', context)


def verify_payment(request, reference):
    response = Transaction.verify(reference)

    if response['status'] and response['data']['status'] == 'success':
        messages.error(request, 'Payment successful')
        return redirect('home')
    else:
        messages.error(request, 'Payment verification failed')
        return redirect('home')


@login_required
def transaction_view(request):
    snack_order = SnackOrder.objects.filter(user=request.user)
    payments = SubscriptionPayment.objects.filter(user=request.user)

    return render(request, 'transaction.html', {'snack_order': snack_order, 'payments': payments})
