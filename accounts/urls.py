from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('ask_bielik/', views.ask_bielik, name='ask_bielik'),
]
