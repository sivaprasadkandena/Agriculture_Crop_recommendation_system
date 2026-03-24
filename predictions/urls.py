from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('', views.home, name='home'),
    path('prediction/', views.dashboard, name='dashboard'),
    path('download/', views.download_results, name='download_results'),
    path('history/', views.history, name='history'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
]