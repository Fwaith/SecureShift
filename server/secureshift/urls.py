"""
URL configuration for secureshift project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import login, logout, register, update_user, verify_otp, users_me
from habitability.views import get_neighbourhoods

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/register', register, name='register'),
    path('api/v1/auth/verify-otp', verify_otp, name='verify_otp'),
    path('api/v1/auth/login', login, name='login'),
    path('api/v1/auth/logout', logout, name='logout'),
    path('api/v1/users/me/update', update_user, name='update_user'),
    path('api/v1/users/me', users_me, name='users_me'),
    path('api/v1/neighbourhoods', get_neighbourhoods, name='get_neighbourhoods'),
]
