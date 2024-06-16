import io
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from paystackapi.transaction import Transaction

from Cinema.models import Subscription, SubscriptionType, MovieOrder, Snack, Restaurant, SnackOrder, \
    SubscriptionPayment, Movie, Seat

# Import libraries for API requests and YouTube trailer lookup (replace with your preferred methods)
import requests
from youtubesearchpython import VideosSearch

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

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

    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for failed requests
        movie_data = response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error fetching movie details for ID {movie_id}: {e}")
        return redirect('movie_detail')

    movie, created = Movie.objects.get_or_create(external_id=movie_id, title=movie_data['original_title'])

    # Handle form submission
    if request.method == 'POST':
        snack_id = request.POST['snack']
        restaurant_id = request.POST['restaurant']
        quantity = request.POST['quantity']
        seat_no = request.POST['seat_no']
        date = request.POST['date']

        restaurant = Restaurant.objects.get(id=restaurant_id)
        snack = Snack.objects.get(id=snack_id)

        total_price = float(snack.price) * int(quantity)

        response = Transaction.initialize(
            reference=str(uuid.uuid4()),
            amount=total_price * 100,
            email=user.email
        )

        if response['status']:
            snack_order = SnackOrder.objects.create(
                user=user,
                snack=snack,
                restaurant=restaurant,
                quantity=int(quantity),
                total_price=total_price
            )

            seat_order = Seat.objects.create(
                user=user,
                seat_no=seat_no,
                date=date
            )

            MovieOrder.objects.create(
                user=user,
                movie=movie,
                snack=snack_order,
                seat=seat_order,
            )

            messages.success(request, f"Order successfully made.")
            return HttpResponseRedirect(response['data']['authorization_url'])

        # Redirect to confirmation or payment page (replace with your logic)
        return redirect('order_confirmation')

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


def get_available_seats(request):
    """
      Fetches available seats for a given date.

      Returns a list of available seat numbers.
      """
    date = request.POST['date']

    # Get all existing seat reservations for the specified date
    booked_seats = Seat.objects.filter(date=date).values_list('seat_no', flat=True)

    # Create a list of all seats (1-100)
    all_seats = list(range(1, 101))

    # Remove booked seats from the list of all seats
    available_seats = [seat for seat in all_seats if seat not in booked_seats]

    return JsonResponse({'available_seats': available_seats})


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


@login_required
def get_valid_movie_orders(request):
    movie_orders = MovieOrder.objects.filter(is_used=False)

    return render(request, 'movie_order.html', {'movie_orders': movie_orders})


def generate_ticket_image(order):
    """
  Generates a ticket image with order information and a visually appealing design.

  Returns a BytesIO object containing the image data.
  """

    # Card dimensions and base color
    card_width, card_height = 400, 200
    base_color = (226, 174, 174)

    # Create card image
    card = Image.new('RGB', (card_width, card_height), base_color)
    draw = ImageDraw.Draw(card)

    # Load a font (handle potential font errors)
    try:
        font = ImageFont.truetype('arial.ttf', 20)
        big_font = ImageFont.truetype('arial.ttf', 24)
        small_font = ImageFont.truetype('arial.ttf', 12)
    except IOError:
        font = ImageFont.load_default()
        big_font = ImageFont.load_default(size=24.0)
        small_font = ImageFont.load_default(size=12.0)

    # Text positions
    text_positions = {
        'company_name': (card_width // 2 - 50, 30),  # Adjust horizontal position
        'user': (card_width // 2, 70),
        'movie': (card_width // 2, 110),
        'seat_no': (card_width // 2, 150),
        'date': (350, 170),
    }

    # Draw text with gold color and slight blur
    text_color = (255, 215, 0)  # Gold color

    for field, position in text_positions.items():
        text = ''
        if field == "user":
            text = f"{order.user.first_name} {order.user.last_name}"
        elif field == "movie":
            text = f"{order.movie.title}"
        elif field == "seat_no":
            text = f"Seat NO.{order.seat.seat_no}"
        elif field == "date":
            text = f"{order.date}"

        text_width = draw.textlength(text, font=font, font_size=24.0)
        centered_position = (position[0] - text_width // 2, position[1])

        if field == 'company_name':
            text = "MOVIE CINEMA"
            text_parts = text.split()
            draw.text((centered_position[0] + text_width - 23, centered_position[1]), text_parts[0], font=big_font, fill=(0, 0, 0))  # Black for 'MOVIE'
            draw.text((centered_position[0] + text_width + 62, centered_position[1]), text_parts[1], font=big_font,
                      fill=(255, 0, 0))  # Red for 'CINEMA' (adjust spacing)
        elif field == "date":
            draw.text(centered_position, text, font=small_font, fill=(0, 0, 0))
        else:
            draw.text(centered_position, text, font=font, fill=(0, 0, 0))  # Black for other text

    # Save the card as an image
    card_data = io.BytesIO()
    card.save(card_data, format='PNG')
    card_data.seek(0)

    return card_data


@login_required
def download_ticket(request, order_id):
    """
    Creates and returns a downloadable ticket image for a specific order.

    Returns an HTTP response with the image data.
    """
    order = MovieOrder.objects.get(pk=order_id)

    # Generate ticket image using helper function (replace with your implementation)
    ticket_image = generate_ticket_image(order)

    # Set response headers for image download
    response = HttpResponse(ticket_image, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename=ticket_{order.id}.png'

    return response
