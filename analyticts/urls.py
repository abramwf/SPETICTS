from django.urls import path
from analyticts import views

urlpatterns = [
    path('', views.main, name='main'),
]