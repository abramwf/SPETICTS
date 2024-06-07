from django.urls import path
from analyticts import views

from .views import transcribe_audio, save_results,  user_login, user_logout, register #, transcribe_view, transcribe_result,

urlpatterns = [
    path('home', views.main, name='home'),
    path('', views.register, name='register'),
    # path('input', transcribe_view, name='input'),
    # path('transcribe/', transcribe_view, name='transcribe'),
    # path('transcribe_result/', transcribe_result, name='transcribe_result'),
    path('detil-page/<int:pk>/', views.detil_view, name='detil_view'),
    path('input', transcribe_audio, name='input'),
    path('save_results/', save_results, name='save_results'),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name='logout'),
]