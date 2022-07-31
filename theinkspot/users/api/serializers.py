from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from theinkspot.users.models import UserFollow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }


class FollowedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = ("id", "follower_user", "created")


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = ("id", "followed_user", "created")


