from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # WEB
    path('', include('myapp.urls')),

    # AUTH
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # API
    path('api/', include('myapp.api_urls')),
]
