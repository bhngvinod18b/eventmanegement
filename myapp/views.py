from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.cache import cache


from .models import Myevent, Myprofile, Bookevent, Saved_event, Notification, Messages
from .models import Follow, Like

def home(request):
    events = cache.get('home_events')

    if not events:
        events = list(Myevent.objects.all().order_by('-id'))
        cache.set('home_events', events, 60)

    booked_events = []

    if request.user.is_authenticated:
        cache_key = f'home_booked_events_{request.user.id}'
        booked_events = cache.get(cache_key)

        if booked_events is None:
            booked_events = list(
                Bookevent.objects.filter(customer=request.user)
                .values_list('event_id', flat=True)
            )
            cache.set(cache_key, booked_events, 60)
    
    if request.method == 'POST':
        event_id = request.POST.get('event_id') 
        event = get_object_or_404(Myevent, id=id)
        # Delete the event from the database
        event.delete()

        # Invalidate the cache
        cache.delete(cache_key)  # Delete the cache for the specific event
        
        # If the event was in the general event list cache, invalidate that too
        cache.delete(f'event_detail{event_id}')
        cache.delete('home_events')  # Invalidate the cache for the home events list
        cache.delete(f'home_booked_events_{request.user.id}')


    return render(request, 'home.html', {
        'events': events,
        'booked_events': booked_events, 
    })

@login_required
def add_event(request):
    if request.method == 'POST':
        event_name = request.POST.get('event')
        adress = request.POST.get('adress')
        phone = request.POST.get('phone')
        about = request.POST.get('about')
        catogery = request.POST.get('catogery')
        capacity = request.POST.get('capacity', 1)  # default 1 if not provided

        # Convert capacity to integer safely
        try:
            capacity = int(capacity)
            if capacity < 1:
                capacity = 1  # minimum 1
        except ValueError:
            capacity = 1  # fallback if not a number

        # Check required fields
        if event_name and adress and phone and about and catogery:
            Myevent.objects.create(
                event=event_name,
                author=request.user,
                adress=adress,
                phone=phone,
                about=about,
                capacity=capacity,
                catogery=catogery
            )
            messages.success(request, f"Event '{event_name}' added successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'add_event.html')
# Delete event
@login_required
def delete_event(request, id):
    event = cache.get(f'delete_event_event{id}')
    if not event:
     event = get_object_or_404(Myevent, id=id)
     cache.set(f'delete_event_event{id}', event, 60)
    if request.method == 'POST':
        event.delete()
        cache.delete(f'delete_event_event_{id}')
        return redirect('home')
    return render(request, 'delete.html', {'event': event})

from django.db.models import Q

def search_event(request):
    
    events = []
    booked_events = []

    if request.method == 'POST':
        search_input = request.POST.get('search_input', '').strip()
        search_category = request.POST.get('search_category', '').strip()

        # Start with all events
        qs = Myevent.objects.select_related('author')

        # Filter by search_input
        if search_input:
            if search_input.isdigit():
                qs = qs.filter(id=int(search_input))
            else:
                qs = qs.filter(event__icontains=search_input)

        # Filter by category
        if search_category:
            qs = qs.filter(catogery=search_category)

        events = qs

    # For logged-in users, find which events are already booked
    if request.user.is_authenticated:
        booked_events = Bookevent.objects.filter(
            customer=request.user
        ).values_list('event_id', flat=True)

    return render(request, 'search.html', {
        'events': events,
        'booked_events': booked_events
    })
# User login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is invalid')

    return render(request, 'login.html')


# User logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


# User registration
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})




@login_required
def profile(request):

    profile = Myprofile.objects.filter(user=request.user).first()

    if request.method == 'POST':

        if profile:
            # UPDATE existing profile
            profile.name = request.POST.get('name')
            profile.customer_phone = request.POST.get('customer_phone')
            profile.customer_adress = request.POST.get('customer_adress')
            profile.gmail = request.POST.get('gmail')
            profile.save()

        else:
            # CREATE new profile
            profile = Myprofile.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                customer_phone=request.POST.get('customer_phone'),
                customer_adress=request.POST.get('customer_adress'),
                gmail=request.POST.get('gmail')
            )

        return redirect('home')

    return render(request, 'profile.html', {
        'profile': profile
    })


@login_required
def book_event(request, id):
    event = cache.get(f'book_event_event{id}')
    if not event:
        event = get_object_or_404(Myevent, id=id)
    if event.author == request.user:
        messages.error(request, "You cannot book your own event")
        return redirect('home')
    booking_total = Bookevent.objects.filter(event=event).count()
    if booking_total >= event.capacity:
        messages.error(request, "event is full you cant book")
        return redirect('home')
    booking = Bookevent.objects.filter(event=event, customer=request.user).first()
    if booking:
        # ✅ CANCEL booking
        booking.delete()
        messages.success(request, "Booking cancelled successfully")
    else:
        # ✅ CREATE booking
        Bookevent.objects.create(
            event=event,
            customer=request.user,
            is_booked=True
        )
        messages.success(request, "Event booked successfully")
        Notification.objects.create(user=event.author,   
                                    author=request.user, 
                                    text=f"{request.user.username} booked your event '{event.event}'",
                                    event=event,
                                    link=f"/event/{event.id}/")
        
        
    return redirect('home')

from django.core.cache import cache

# Save/unsave an event
@login_required
def saved_event(request, id):
    event = cache.get(f'saved_event_event{id}')
    if not event:
        event = get_object_or_404(Myevent, id=id)
        cache.set(f'saved_event_event{id}', event, 60)
    saved, created = Saved_event.objects.get_or_create(user=request.user, event=event)
    if not created:
        # If already exists, remove it
        saved.delete()
        cache.delete(f'saved_event_event{id}')
    return redirect('home')


# List saved events for the current user
@login_required
def my_saved(request):
    cache_key = f'my_saved_saved_events_{request.user.id}'
    saved_events = cache.get(cache_key)
    if not saved_events:
        saved_events = Saved_event.objects.select_related('event', 'event__author').filter(user=request.user)
        cache.set(cache_key, saved_events, 60*20)
    return render(request, 'saved.html', {'saved_events': saved_events})
@login_required
def my_bookings(request):
    cache_key = f'my_bookings_bookings_{request.user.id}'
    bookings = cache.get(cache_key)
    if not bookings:
        bookings = Bookevent.objects.select_related('event', 'event__author').filter(customer=request.user)
        cache.set(cache_key, bookings, 60*20)
    return render(request, 'my_bookings.html', {
        'bookings': bookings
    })

@login_required
def notification(request):
    cache_key = f'notification_notifications'
    notifications = cache.get(cache_key)
    if not notifications:
        notifications = Notification.objects.all()
        cache.set(cache_key, notifications, 60*20)
    return render(request, 'notifications.html', {'notifications': notifications})
@login_required
def event_detail(request, id):
    cache_key = f'event_detail{id}'
    event = cache.get(cache_key)
    ratings = None
    if not event:
        event = get_object_or_404(Myevent, id=id)
        cache.set(cache_key, event, 60)
    
    return render(request, 'event_detail.html', {'event': event})

@login_required
def my_activity(request):
    events = cache.get('my_activity_events')
    if not events:
        events = list(Myevent.objects.filter(author=request.user).all().order_by('id'))
        cache.set('my_activity_events', events, 60*20)
    bookings = cache.get('my_activity_bookings')
    if not bookings:
        bookings = list(Bookevent.objects.filter(customer=request.user).all().order_by('-created_at'))
        cache.set('my_activity_bookings', bookings, 60*20)
    saved = cache.get('my_activity_saved')
    if not saved:
        saved = list(Saved_event.objects.filter(user=request.user).all().order_by('id'))
        cache.set('my_activity_saved', saved, 60*20)
    return render(request, 'my_activity.html', {'events': events, 'bookings': bookings,
                                                'saved': saved})
    
@login_required
def send_messages(request, user_id):
    
    reciver = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        text = cache.get('send_messages_text')
        if not text:
            text = request.POST.get('text')
        if text:
            Messages.objects.create(sender=request.user,
                                  reciver=reciver,
                                  text=text)
            cache.delete('send_messages_text')
            return redirect('inbox')
    return render(request, 'recived_messages.html', {'reciver': reciver})

@login_required
def inbox(request):
    messages = cache.get('inbox_messages')
    if not messages:
        messages = list(Messages.objects.select_related('sender').filter(reciver=request.user).order_by("-created_at"))
        cache.set('inbox_messages', messages, 60*20)
    return render(request, "my_messages.html", {"messages": messages})

from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from .models import Myevent, Saved_event, Bookevent, User, Follow, Like


@login_required
def settings_dashboard(request):

    # 1. Most saved events
    top_saved = cache.get('settings_dashbard_top_saved')
    if not top_saved:
        top_saved = list(Saved_event.objects.annotate(
        saved_count=Count('event')
    ).order_by('-saved_count')[:5])
        cache.set('settings_dashboard_top_saved', top_saved, 60)

    # 2. Top users by bookings
    top_users_by_bookings = cache.get('settings_dashboard_top_users_by_bookings')
    if not top_users_by_bookings:
        top_users_by_bookings = list(Myevent.objects.annotate(
        booking_count=Count('bookevent')
    ).order_by('-booking_count'))
        cache.set('settings_dashboard_top_saved', top_users_by_bookings, 60)

    # 3. Top categories
    top_categories = cache.get('settings_dashboard_top_categories')
    if not top_categories:
        top_categories = list(Myevent.objects.values('catogery').annotate(
        total=Count('id')
    ).order_by('-total'))
        cache.set('settings_dashboard_top_categories', top_categories, 60)

    # 4. No booking events
    no_booking = cache.get('settings_dashboard_no_booking')
    if not no_booking:
        no_booking = list(Myevent.objects.annotate(
        total_booking=Count('bookevent')
    ).filter(total_booking=0))
        cache.set('settings_dashboard_no_booking', no_booking, 60)

    # 5. Full events
    full_events = cache.get('settings_dashboard_full_events')
    if not full_events:
        full_events = list(Myevent.objects.annotate(
        booked=Count('bookevent')
    ).filter(booked__gte=F('capacity')))
        cache.set('settings_dashboard_full_events', full_events, 60)

    # 6. Most booked events
    most_booked = cache.get('settings_dashboard_most_booked')
    if not most_booked:
        most_booked = list(Myevent.objects.annotate(
        booked=Count('bookevent')
    ).order_by('-booked'))
        cache.set('settings_dashboard_most_booked', most_booked, 60)

    # 7. Trending (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    trending = cache.get('settings_dashboard_trending')
    if not trending:
        trending = list(Myevent.objects.filter(
        bookevent__created_at__gte=seven_days_ago
    ).annotate(
        trending_count=Count('bookevent')
    ).order_by('-trending_count'))
        cache.set('settings_dashboards_trending', trending, 60)

    # 8. Top users by followers
    top_users_by_followers = cache.get('settings_dashboard_top_users_by_followers')
    if not top_users_by_followers:
        top_users_by_followers = list(User.objects.annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count'))
        cache.set('settings_dashboard_top_users_by_followers', top_users_by_followers, 60)

    return render(request, 'settings_dashboard.html', {
        'top_saved': top_saved,
        'top_users_by_bookings': top_users_by_bookings,
        'top_categories': top_categories,
        'no_booking': no_booking,
        'full_events': full_events,
        'most_booked': most_booked,
        'trending': trending,
        'top_users_by_followers': top_users_by_followers,
    })
    
@login_required
def track_event(request):
    events = Myevent.objects.annotate(booked_count=Count('bookevent')).order_by('-booked_count')[:5]
    return render(request, 'track.html', {'events': events})
    
from rest_framework import viewsets
from .serializers import Myeventserializers, Likeserializers, Followserializers, Saved_eventserializers
from .serializers import Bookeventserializers
class MyeventViewSet(viewsets.ModelViewSet):
    queryset = Myevent.objects.all()
    serializer_class = Myeventserializers
    lookup_field = 'phone'
    search_field = ['author', 'event']

class LiketViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = Likeserializers
    lookup_field = 'event'
    search_field = ['event', 'user']
    
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = Followserializers
    lookup_field = 'following'
    search_field = ['following__username', 'follower__username']

class Saved_eventViewSet(viewsets.ModelViewSet):
    queryset = Saved_event.objects.all()
    serializer_class = Saved_eventserializers
    lookup_field = 'event'
    search_field = ['event', 'user']
    
class BookeventViewSet(viewsets.ModelViewSet):
    queryset = Bookevent.objects.all()
    serializer_class = Bookeventserializers
    lookup_field = 'event'
    search_field = ['event', 'customer']
    
    
