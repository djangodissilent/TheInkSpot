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


class FollowingSerializer(serializers.ModelSerializer):
    followed = UserSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = ("id", "followed", "created")


class FollowerSerializer(serializers.ModelSerializer):
    followers = UserSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = ("id", "followers", "created")
