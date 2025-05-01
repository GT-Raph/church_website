from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('event/', views.event, name='event'),
    path('sermons/', views.sermons, name='sermons'),
    path('giving/', views.giving, name='giving'),
    path('register/', views.register_member, name='register'),
]
