from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_comment),   # POST /api/v1/comments
]