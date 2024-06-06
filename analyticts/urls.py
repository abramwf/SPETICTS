from django.urls import path
from analyticts import views
from .views import transcribe_view, transcribe_result, transcribe_audio, save_results

urlpatterns = [
    path('', views.main, name='home'),
    # path('input', transcribe_view, name='input'),
    # path('transcribe/', transcribe_view, name='transcribe'),
    # path('transcribe_result/', transcribe_result, name='transcribe_result'),
    path('detil-page/<int:pk>/', views.detil_view, name='detil_view'),
    path('input', transcribe_audio, name='input'),
    path('save_results/', save_results, name='save_results'),
]