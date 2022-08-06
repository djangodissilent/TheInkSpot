from django.conf import settings
from django.urls import path
from .views import FollowersView, FollowingsView, FollowView, UnfollowView


urlpatterns = [
    path("followers/<str:username>", FollowersView.as_view(), name="followers"),
    path("followings/<str:username>", FollowingsView.as_view(), name="user-following"),
    path("follow/", FollowView.as_view(), name="user-follow"),
    path("unfollow/", UnfollowView.as_view(), name="user-unfollow"),
]
