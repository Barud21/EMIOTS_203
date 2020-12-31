from django.urls import path

from .views import (
    TweetListView
)

urlpatterns = [
    path('tweets/',  TweetListView.as_view(), name='tweet-list')
]
