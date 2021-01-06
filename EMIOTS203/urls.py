from django.urls import path

from .views import (
    tweetsChartsView
)

urlpatterns = [
    path('tweets/',  tweetsChartsView)

]
