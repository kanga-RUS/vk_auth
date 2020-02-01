from django.urls import path

from .views import HomePageView, search

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('search/', search, name='search'),
]
