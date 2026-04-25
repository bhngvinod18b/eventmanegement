from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # Events
    path('add/', views.add_event, name='add_event'),
    path('delete/<int:id>/', views.delete_event, name='delete_event'),
    path('search/', views.search_event, name='search_event'),
    path('book/<int:id>/', views.book_event, name='book_event'),
    
    # Saved events
    path('save/<int:id>/', views.saved_event, name='saved_event'),
    path('my_saved/', views.my_saved, name='my_saved'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('notifications/', views.notification, name='notifications'),
    path('event/<int:id>/', views.event_detail, name='event_detail'),
    path('my-activity/', views.my_activity, name='my_activity'),
    path('send-message/<int:user_id>/', views.send_messages, name='send_messages'),
    path('inbox/', views.inbox, name='inbox'),
    path('settings/', views.settings_dashboard, name='settings'),
    path('track/', views.track_event, name='track_event'), 
     
]
