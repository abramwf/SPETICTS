from django.urls import path
from analyticts import views
from .views import main, detil_view, transcribe_audio, save_results, other_view

urlpatterns = [
    path('', main, name='home'),
    path('detil-page/<int:pk>/', detil_view, name='detil_view'),
    path('input', transcribe_audio, name='input'),
    path('save_results/', save_results, name='save_results'),
    path('other/', other_view, name='other_view'),
]