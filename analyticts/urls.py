from django.urls import path
from analyticts import views
from django.conf import settings
from django.conf.urls.static import static
from .views import transcribe_audio, save_results, user_login, user_logout  #transcribe_view, transcribe_result, profile, delete_profile_image

urlpatterns = [
    path("", views.register, name='register'),
    path('home', views.main, name='home'),
    path('input', transcribe_audio, name='input'),
    path('save_results/', save_results, name='save_results'),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    # path('profile/delete_image/', delete_profile_image, name='delete_profile_image'),
    # path('transcribe/', transcribe_view, name='transcribe'),
    # path('transcribe_result/', transcribe_result, name='transcribe_result'),
] 

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)